//! Private offline route fixture. Native engines own every economic and replay operation.
use std::{any::Any, cell::RefCell, collections::{BTreeMap, BTreeSet}, fmt, fs, path::Path, process::Command, rc::Rc,
    sync::{Arc, Mutex}, time::Duration};
use anyhow::{Result, ensure};
use nautilus_backtest::{config::{BacktestEngineConfig, SimulatedVenueConfig}, engine::BacktestEngine};
use nautilus_common::{cache::{Cache, CacheConfig}, cache::database::CacheDatabaseFactory,
    clock::{Clock, VirtualClock}, enums::Environment, actor::DataActor,
    msgbus::{self, BusTap, MStr, ShareableMessageHandler, Topic, Endpoint}};
use nautilus_core::{UUID4, UnixNanos};
use nautilus_event_store::{EventStoreEntry, EventStoreError, EventStoreLifecycle, EventStoreLifecycleOptions,
    RunManifest, RunStatus, ScanDirection, SnapshotAnchor, apply_cache_replay_entry, compute_snapshot_content_hash,
    open_event_store_replay_source, restore_cache_snapshot_blob};
use nautilus_event_store::backend::{AppendEntry, EventStore, IndexKind, RedbBackend};
use nautilus_event_store::capture::encode_order_filled;
use nautilus_execution::models::fee::{FeeModelAny, MakerTakerFeeModel};
use nautilus_infrastructure::redis::cache::RedisCacheConfig;
use nautilus_model::{accounts::{Account, AccountAny}, data::{Data, FundingRateUpdate, QuoteTick}, enums::{AccountType, BookType, OmsType, OrderSide},
    identifiers::{InstrumentId, StrategyId, Symbol, TraderId, Venue},
    instruments::{CryptoPerpetual, Instrument, InstrumentAny}, orders::Order, events::{FundingSettlement, OrderEventAny, OrderFilled},
    types::{Currency, Money, Price, Quantity}};
use nautilus_portfolio::Portfolio;
use nautilus_system::{RegisteredComponents, event_store::{EventStoreConfig, RunIdentity}};
use nautilus_trading::{Strategy, StrategyConfig, StrategyCore, nautilus_strategy};
use rust_decimal::Decimal;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const SOURCE: &str = "55c0e82053142bce3a5cba4de4221d3929c2d3bc";
const SCENARIOS: &[&str] = &["round_trip", "reversal", "multi_cycle", "open",
    "funding_long_pos", "funding_long_neg", "funding_short_pos", "funding_short_neg", "funding_flat_pos",
    "funding_flat_neg", "funding_duplicate", "funding_missing", "funding_no_boundary", "funding_stale",
    "funding_cross_instrument", "liquidation_on_195", "liquidation_off_195", "liquidation_on_200",
    "liquidation_off_200", "liquidation_on_250", "liquidation_off_250"];
fn hash(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
fn binary_hash() -> Result<String> { Ok(hash(&fs::read(std::env::current_exe()?)?)) }
fn lock_hash() -> String { hash(include_bytes!("../Cargo.lock")) }
fn write(path: &Path, value: &Value) -> Result<()> { fs::write(path, serde_json::to_vec_pretty(value)?)?; Ok(()) }

// Fixture trust root is supplied by the owning controller, outside the recovered stores.
// A digest proves pairing/integrity, not global atomicity or human trading authority.
fn authority(checkpoint: &Value) -> Result<()> {
    ensure!(checkpoint["source"] == SOURCE, "SOURCE_IDENTITY");
    ensure!(checkpoint["binary_sha256"] == binary_hash()?, "BINARY_IDENTITY");
    ensure!(checkpoint["cargo_lock_sha256"] == lock_hash(), "LOCK_IDENTITY");
    ensure!(checkpoint["checkpoint"] == "NATIVE_SEALED_AND_CACHE_DATABASE_CLOSED", "UNACKNOWLEDGED_CHECKPOINT");
    ensure!(checkpoint["lifecycle"] == json!(["before_seal", "after_seal", "after_drain", "acknowledged"]), "LIFECYCLE_ORDER");
    ensure!(checkpoint["pid"].as_u64().is_some_and(|p| p > 0), "PRODUCER_PID");
    for field in ["trader", "instance_id", "run_id"] {
        ensure!(checkpoint[field].as_str().is_some_and(|s| !s.is_empty()), "MISSING_IDENTITY: {field}");
    }
    ensure!(checkpoint["watermark"].as_u64().is_some_and(|n| n > 0), "STALE_WATERMARK");
    ensure!(checkpoint["run_error"].is_null(), "NATIVE_RUN_FAILED");
    for field in ["redis_contents", "source_files", "state", "manifest"] {
        ensure!(checkpoint[field].as_object().is_some_and(|v| !v.is_empty()), "MISSING_RECEIPT: {field}");
    }
    let fills = checkpoint["state"]["fills"].as_array().ok_or_else(|| anyhow::anyhow!("MISSING_FILLS"))?;
    ensure!(!fills.is_empty(), "MISSING_FILLS");
    let mut ids = BTreeSet::new();
    for fill in fills {
        ensure!(ids.insert((fill["order_id"].to_string(), fill["trade_id"].to_string())), "REPEATED_OR_CONFLICTING_FILL");
    }
    Ok(())
}

// Producer-retained native anchors are provenance only. Each must name its contiguous archived
// frame, hash natively to that frame's exact producer bytes, advance the native watermark and
// end at the native latest anchor. Missing, reordered, stale, altered or cross-paired chains refuse.
fn anchor_chain(checkpoint: &Value, latest: Option<&SnapshotAnchor>, durable: u64) -> Result<Vec<SnapshotAnchor>> {
    let chain: Vec<SnapshotAnchor> = serde_json::from_value(checkpoint["anchor_chain"].clone())
        .map_err(|_| anyhow::anyhow!("ARCHIVE_CONTINUITY_BLOCKED: missing native anchor chain"))?;
    let frames = checkpoint["state"]["snapshots"].as_array().ok_or_else(|| anyhow::anyhow!("MISSING_ARCHIVE_IDENTITIES"))?;
    ensure!(chain.len() == frames.len(), "ARCHIVE_CONTINUITY_BLOCKED: {} anchors for {} frames", chain.len(), frames.len());
    ensure!(chain.last() == latest, "ARCHIVE_CONTINUITY_BLOCKED: chain does not end at native latest anchor");
    let mut next = BTreeMap::<&str, u64>::new();
    let mut previous = 0;
    for anchor in &chain {
        let (prefix, index) = anchor.blob_ref.rsplit_once('/')
            .ok_or_else(|| anyhow::anyhow!("ARCHIVE_CONTINUITY_BLOCKED: blob reference"))?;
        let position = prefix.strip_prefix("cache://position-snapshots/")
            .ok_or_else(|| anyhow::anyhow!("ARCHIVE_CONTINUITY_BLOCKED: blob reference"))?;
        let expected = next.entry(position).or_default();
        ensure!(index == expected.to_string(), "ARCHIVE_CONTINUITY_BLOCKED: frame {position}/{index} is not frame {expected}");
        let frame = frames.iter().find(|f| f["position_id"] == position && f["index"] == json!(*expected))
            .ok_or_else(|| anyhow::anyhow!("ARCHIVE_CONTINUITY_BLOCKED: anchored frame absent"))?;
        *expected += 1;
        let bytes: Vec<u8> = serde_json::from_value(frame["bytes"].clone())?;
        ensure!(frame["sha256"] == hash(&bytes), "ARCHIVE_CONTINUITY_BLOCKED: frame bytes");
        ensure!(compute_snapshot_content_hash(&bytes) == anchor.content_hash, "ARCHIVE_CONTINUITY_BLOCKED: anchor hash differs from frame");
        ensure!(anchor.high_watermark > previous && anchor.high_watermark <= durable, "ARCHIVE_CONTINUITY_BLOCKED: anchor watermark");
        previous = anchor.high_watermark;
    }
    Ok(chain)
}

// Open exposure may be priced only by the exact producer-observed native quote. It is applied to the
// disposable in-memory cache; missing, altered, stale or mismatched market context refuses.
fn market_context(checkpoint: &Value) -> Result<Option<QuoteTick>> {
    let positions = checkpoint["state"]["positions"].as_array().ok_or_else(|| anyhow::anyhow!("MISSING_POSITIONS"))?;
    let open = positions.iter().filter(|p| p["closed"] != true).collect::<Vec<_>>();
    if open.is_empty() { return Ok(None); }
    let context = &checkpoint["market_context"];
    let native = context["native"].as_str()
        .ok_or_else(|| anyhow::anyhow!("OPEN_EXPOSURE_REQUIRES_RECONCILIATION: missing producer quote"))?;
    ensure!(context["sha256"] == hash(native.as_bytes()), "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote bytes");
    for field in ["pid", "instance_id", "run_id"] {
        ensure!(context["source"][field] == checkpoint[field], "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote source {field}");
    }
    let quote: QuoteTick = serde_json::from_str(native)?;
    ensure!(context["instrument_id"] == quote.instrument_id.to_string()
        && context["ts_event"] == quote.ts_event.as_u64(), "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote identity");
    ensure!(quote.bid_price.as_decimal() > Decimal::ZERO && quote.bid_price <= quote.ask_price,
        "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote prices");
    ensure!(checkpoint["manifest"]["end_ts_init"].as_u64().is_some_and(|end| quote.ts_event.as_u64() <= end),
        "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote after seal");
    for position in open {
        ensure!(position["native"]["instrument_id"] == quote.instrument_id.to_string(), "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: quote instrument");
        ensure!(position["native"]["ts_last"].as_u64().is_some_and(|last| quote.ts_event.as_u64() >= last),
            "OPEN_EXPOSURE_REQUIRES_RECONCILIATION: stale quote");
    }
    Ok(Some(quote))
}

fn redis_read(args: &[&str]) -> Result<Value> {
    let port = std::env::var("CPW_ROUTE_REDIS_PORT").unwrap_or_else(|_| "6397".into());
    ensure!(["6397", "6398"].contains(&port.as_str()), "PRIVATE_PORT_REQUIRED");
    let output = Command::new("redis-cli").args(["-h", "127.0.0.1", "-p", &port, "--json"])
        .args(args).output()?;
    ensure!(output.status.success(), "REDIS_READ: {}", String::from_utf8_lossy(&output.stderr));
    Ok(serde_json::from_slice(&output.stdout)?)
}

fn redis_contents() -> Result<Value> {
    let keys = redis_read(&["KEYS", "*"])?;
    let mut rows = BTreeMap::new();
    for key in keys.as_array().ok_or_else(|| anyhow::anyhow!("REDIS_KEYS"))? {
        let key = key.as_str().ok_or_else(|| anyhow::anyhow!("REDIS_KEY_TYPE"))?;
        let kind = redis_read(&["TYPE", key])?;
        let mut value = match kind.as_str() {
            Some("string") => redis_read(&["GET", key])?,
            Some("list") => redis_read(&["LRANGE", key, "0", "-1"] )?,
            Some("set") => redis_read(&["SMEMBERS", key])?,
            Some("hash") => redis_read(&["HGETALL", key])?,
            _ => anyhow::bail!("REDIS_RECORD_TYPE"),
        };
        if kind == "set" { value.as_array_mut().unwrap().sort_by_key(Value::to_string); }
        rows.insert(key.to_string(), json!({"type": kind, "value": value}));
    }
    Ok(serde_json::to_value(rows)?)
}

fn source_files(root: &Path) -> Result<Value> {
    fn visit(root: &Path, path: &Path, rows: &mut BTreeMap<String, String>) -> Result<()> {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let kind = entry.file_type()?;
            ensure!(!kind.is_symlink(), "SOURCE_SYMLINK");
            if kind.is_dir() { visit(root, &entry.path(), rows)?; }
            else { rows.insert(entry.path().strip_prefix(root)?.to_string_lossy().into(), hash(&fs::read(entry.path())?)); }
        }
        Ok(())
    }
    let mut rows = BTreeMap::new();
    visit(root, root, &mut rows)?;
    Ok(serde_json::to_value(rows)?)
}

fn boundary(root: &Path, name: &str, lifecycle: &mut Vec<String>) -> Result<()> {
    lifecycle.push(name.into());
    write(&root.join("boundary.json"), &json!({"pid": std::process::id(), "boundary": name,
        "lifecycle": lifecycle, "binary_sha256": binary_hash()?}))?;
    if std::env::var("CPW_CRASH_BOUNDARY").ok().as_deref() == Some(name) {
        loop { std::thread::sleep(Duration::from_millis(50)); }
    }
    Ok(())
}
fn instrument() -> InstrumentAny {
    CryptoPerpetual::builder().instrument_id(InstrumentId::from("BTCUSDT-PERP.SIM"))
        .raw_symbol(Symbol::from("BTCUSDT"))
        .base_currency(Currency::BTC()).quote_currency(Currency::USDT()).settlement_currency(Currency::USDT())
        .is_inverse(false).price_precision(2).size_precision(3)
        .price_increment(Price::from("0.01")).size_increment(Quantity::from("0.001"))
        .margin_init(Decimal::new(1, 1)).margin_maint(Decimal::new(5, 2))
        .ts_event(UnixNanos::default()).ts_init(UnixNanos::default()).build().unwrap().into()
}
// N2-06 controlled fixture input only: native funding-rate updates. Settlement, sign, basis and
// cash effect belong to the native exchange; boundary 1.5s falls between the 1s and 2s quotes.
fn funding_updates(scenario: &str, id: InstrumentId) -> Vec<Data> {
    let t = |ms: u64| UnixNanos::from(1_800_000_000_000_000_000u64 + ms * 1_000_000);
    let rate = if scenario.ends_with("_neg") { Decimal::new(-1, 2) } else { Decimal::new(1, 2) };
    let update = |id, at, boundary| Data::FundingRate(FundingRateUpdate::new(id, rate, None, boundary, t(at), t(at)));
    let boundary = Some(t(1500));
    match scenario {
        "funding_missing" => vec![],
        "funding_no_boundary" => vec![update(id, 500, None)],
        "funding_stale" => vec![update(id, 1600, boundary)],
        "funding_cross_instrument" => vec![update(InstrumentId::from("ETHUSDT-PERP.SIM"), 500, boundary)],
        "funding_duplicate" => vec![update(id, 500, boundary), update(id, 1200, boundary), update(id, 2500, boundary)],
        s if s.starts_with("funding_") => vec![update(id, 500, boundary)],
        _ => vec![],
    }
}

fn config() -> CacheConfig { CacheConfig { use_trader_prefix: true, use_instance_id: false,
    flush_on_start: false, buffer_interval_ms: Some(0), ..Default::default() } }
fn db(rt: &tokio::runtime::Runtime, trader: TraderId, instance: UUID4, restore: bool)
    -> Result<Box<dyn nautilus_common::cache::database::CacheDatabaseAdapter>> {
    let port = std::env::var("CPW_ROUTE_REDIS_PORT").unwrap_or_else(|_| "6397".into()).parse::<u16>()?;
    ensure!([6397, 6398].contains(&port), "only owned fixture Redis ports permitted");
    // Restores connect as the clone's controller-created read-only ACL user, so native Portfolio
    // initialization updates only the disposable in-memory cache and Redis itself denies any write.
    let (username, password) = if restore {
        let user = std::env::var("CPW_ROUTE_REDIS_READONLY_USER").map_err(|_| anyhow::anyhow!("READ_ONLY_RESTORE_CONNECTION_REQUIRED"))?;
        let rules = redis_read(&["ACL", "GETUSER", &user])?.to_string();
        ensure!(rules.contains("-@write"), "READ_ONLY_RESTORE_CONNECTION_REQUIRED");
        (Some(user), Some(std::env::var("CPW_ROUTE_REDIS_READONLY_TOKEN")?))
    } else { (None, None) };
    let redis = RedisCacheConfig { host: Some("127.0.0.1".into()), port: Some(port), username, password,
        number_of_retries: 0, connection_timeout: 2, response_timeout: 2, ..Default::default() };
    rt.block_on(redis.create(trader, instance, config()))
}

// Pass-through observer of the native redb backend. The native writer derives each anchor's
// durable watermark and the native lifecycle its content hash; this only retains accepted anchors.
struct AnchorTap { inner: RedbBackend, chain: Arc<Mutex<Vec<SnapshotAnchor>>> }
impl EventStore for AnchorTap {
    fn open_run(&mut self, manifest: RunManifest) -> Result<(), EventStoreError> { self.inner.open_run(manifest) }
    fn append_batch(&mut self, entries: &[AppendEntry]) -> Result<u64, EventStoreError> { self.inner.append_batch(entries) }
    fn scan_range(&self, from: u64, to: u64, direction: ScanDirection) -> Result<Vec<EventStoreEntry>, EventStoreError> {
        self.inner.scan_range(from, to, direction)
    }
    fn scan_seq(&self, seq: u64) -> Result<Option<EventStoreEntry>, EventStoreError> { self.inner.scan_seq(seq) }
    fn lookup(&self, kind: IndexKind, key: &str) -> Result<Option<u64>, EventStoreError> { self.inner.lookup(kind, key) }
    fn iter_index_keys(&self, kind: IndexKind) -> Result<Vec<(String, u64)>, EventStoreError> { self.inner.iter_index_keys(kind) }
    fn record_snapshot_anchor(&mut self, anchor: SnapshotAnchor) -> Result<(), EventStoreError> {
        self.inner.record_snapshot_anchor(anchor.clone())?;
        self.chain.lock().unwrap().push(anchor);
        Ok(())
    }
    fn latest_snapshot_anchor(&self) -> Result<Option<SnapshotAnchor>, EventStoreError> { self.inner.latest_snapshot_anchor() }
    fn seal(&mut self, status: RunStatus) -> Result<(), EventStoreError> { self.inner.seal(status) }
    fn manifest(&self) -> Result<RunManifest, EventStoreError> { self.inner.manifest() }
    fn high_watermark(&self) -> Result<u64, EventStoreError> { self.inner.high_watermark() }
}

struct Script { core: StrategyCore, id: InstrumentId, scenario: String, step: usize }
nautilus_strategy!(Script);
impl fmt::Debug for Script {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { f.debug_struct("Script").finish() }
}
impl DataActor for Script {
    fn on_start(&mut self) -> Result<()> { self.subscribe_quotes(self.id, None, None); Ok(()) }
    fn on_quote(&mut self, _: &QuoteTick) -> Result<()> {
        let action = match self.scenario.as_str() {
            "reversal" => vec![(OrderSide::Buy, "1.000"), (OrderSide::Sell, "2.000"), (OrderSide::Buy, "1.000")],
            "multi_cycle" => vec![(OrderSide::Buy, "1.000"), (OrderSide::Sell, "2.000"),
                (OrderSide::Buy, "2.000"), (OrderSide::Sell, "1.000")],
            "open" => vec![(OrderSide::Buy, "1.000")],
            s if s.starts_with("liquidation_") => vec![(OrderSide::Sell, "100.000")],
            s if s.starts_with("funding_short") => vec![(OrderSide::Sell, "1.000")],
            s if s.starts_with("funding_flat") => vec![(OrderSide::Buy, "1.000"), (OrderSide::Sell, "1.000")],
            s if s.starts_with("funding_") => vec![(OrderSide::Buy, "1.000")],
            _ => vec![(OrderSide::Buy, "1.000"), (OrderSide::Sell, "0.000"), (OrderSide::Sell, "1.000")],
        };
        if self.step < action.len() {
            let (side, qty) = action[self.step]; self.step += 1;
            if qty != "0.000" {
                let order = self.order().market(self.id, side, Quantity::from(qty),
                    None, None, None, None, None, None, None);
                self.submit_order(order, None, None, None)?;
            }
        }
        Ok(())
    }
}

fn observation(cache: &Rc<RefCell<Cache>>, portfolio: &mut Portfolio) -> Result<Value> {
    let id = instrument().id();
    let pnl = portfolio.realized_pnl(&id).map(|x| x.as_decimal().to_string());
    let unrealized = portfolio.unrealized_pnl(&id).map(|x| x.as_decimal().to_string());
    let exposure = portfolio.net_exposure(&id, None, None, None).map(|x| x.as_decimal().to_string());
    let cache = cache.borrow();
    let positions = cache.positions(None, None, None, None, None);
    let orders = cache.orders(None, None, None, None, None);
    let mut snapshots = Vec::new();
    let mut position_rows = Vec::new();
    for position in positions {
        let mut native = serde_json::to_value(&*position)?;
        // JSON's default float parser changes some ULPs. Compare decimal economics and
        // exact native events/quantities; retain approximate metrics in a separate witness.
        for field in ["avg_px_close", "avg_px_open", "realized_return", "signed_qty"] {
            native.as_object_mut().unwrap().remove(field);
        }
        let bytes = cache.position_snapshot_bytes(&position.id).unwrap_or_default();
        for (index, frame) in bytes.into_iter().enumerate() { snapshots.push(json!({"position_id": position.id.to_string(),
            "index": index, "sha256": hash(&frame), "bytes": frame})); }
        position_rows.push(json!({"id": position.id.to_string(), "closed": position.is_closed(),
            "native": native,
            "pnl": position.realized_pnl.map(|x| x.as_decimal().to_string()),
            "trades": position.trade_ids().iter().map(ToString::to_string).collect::<Vec<_>>() }));
    }
    let mut fills = Vec::new();
    for order in &orders {
        for event in order.events() {
            if let OrderEventAny::Filled(fill) = event {
                fills.push(json!({"trade_id": fill.trade_id.to_string(), "order_id": fill.client_order_id.to_string(),
                    "event_id": fill.event_id.to_string(), "payload": serde_json::to_value(fill)?}));
            }
        }
    }
    fills.sort_by_key(|x| x["trade_id"].to_string());
    let mut archived = cache.position_snapshots(None, None).iter().map(|p| json!({
        "id": p.id.to_string(), "closed": p.is_closed(),
        "pnl": p.realized_pnl.map(|x| x.as_decimal().to_string())})).collect::<Vec<_>>();
    archived.sort_by_key(|x| x["id"].to_string());
    snapshots.sort_by_key(|x| x["sha256"].to_string());
    let mut order_rows = orders.iter().map(|order| json!({"id": order.client_order_id().to_string(),
        "status": order.status().to_string(), "filled": order.filled_qty().to_string(),
        "events": order.events().len()})).collect::<Vec<_>>();
    order_rows.sort_by_key(|x| x["id"].to_string());
    position_rows.sort_by_key(|x| x["id"].to_string());
    let accounts = cache.accounts_all_owned();
    fn margins<'a>(rows: impl IntoIterator<Item = (&'a InstrumentId, &'a Money)>) -> Vec<Value> {
        rows.into_iter().map(|(id, x)| json!([id.to_string(), x.as_decimal().to_string()])).collect()
    }
    let account_rows = accounts.iter().map(|account| {
        let mut row = json!({"id": account.id().to_string(),
            "equity": account.balance_total(Some(Currency::USDT())).map(|x| x.as_decimal().to_string()),
            "balances": account.balances().values().map(|b| json!({"currency": b.currency.code.to_string(),
                "total": b.total.as_decimal().to_string(), "locked": b.locked.as_decimal().to_string(),
                "free": b.free.as_decimal().to_string()})).collect::<Vec<_>>()});
        if let AccountAny::Margin(margin) = account {
            row["initial_margins"] = json!(margins(margin.initial_margins().iter()));
            row["maintenance_margins"] = json!(margins(margin.maintenance_margins().iter()));
        }
        row
    }).collect::<Vec<_>>();
    Ok(json!({"portfolio_realized_pnl": pnl, "portfolio_unrealized_pnl": unrealized,
        "portfolio_net_exposure": exposure, "positions": position_rows, "orders": order_rows,
        "accounts": account_rows, "snapshots": snapshots, "archived": archived, "fills": fills}))
}

fn produce(root: &Path, scenario: &str, hold: bool) -> Result<()> {
    fs::create_dir_all(root)?;
    ensure!(!root.join("checkpoint.json").exists(), "checkpoint already exists");
    let rt = tokio::runtime::Runtime::new()?;
    let label = root.file_name().unwrap().to_str().unwrap().replace('_', "");
    let trader = TraderId::new(format!("N2H{label}-001"));
    let mut engine = BacktestEngine::new(BacktestEngineConfig { trader_id: trader,
        bypass_logging: true, run_analysis: false, cache: Some(config()), ..Default::default() })?;
    let instance = engine.kernel().instance_id;
    engine.kernel().cache.borrow_mut().set_database(db(&rt, trader, instance, false)?);
    let clock = engine.kernel().clock.clone();
    let identity = RunIdentity { binary_hash: binary_hash()?, schema_version: 1,
        crate_versions: lock_hash(), config_hash: hash(scenario.as_bytes()),
        feature_flags: vec![SOURCE.into()], ..Default::default() };
    // Same native backend as the default opener, observed at the point each native anchor is accepted.
    let chain = Arc::new(Mutex::new(Vec::new()));
    let tap = chain.clone();
    let options = EventStoreLifecycleOptions::new().with_backend_opener(move |config, manifest| {
        let mut inner = RedbBackend::new(config.base_dir.clone());
        inner.open_run(manifest.clone())?;
        Ok(Box::new(AnchorTap { inner, chain: tap.clone() }))
    });
    let mut store = EventStoreLifecycle::boot_with_options(Some(EventStoreConfig {
        base_dir: root.join("event_store"), identity, ..Default::default() }), instance, clock, options)?;
    store.open(instance, &RegisteredComponents::default(), Environment::Backtest)?;
    engine.kernel().exec_engine.borrow_mut().set_snapshot_anchorer(store.snapshot_anchorer());
    engine.add_venue(SimulatedVenueConfig::builder().venue(Venue::from("SIM"))
        .oms_type(OmsType::Netting).account_type(AccountType::Margin).book_type(BookType::L1_MBP)
        .starting_balances(vec![Money::from("10000 USDT")])
        .base_currency(Currency::USDT()).default_leverage(Decimal::ONE)
        .fee_model(FeeModelAny::MakerTaker(MakerTakerFeeModel::new(Decimal::new(4, 4), Decimal::new(4, 4))).into())
        .liquidation_enabled(scenario.starts_with("liquidation_on"))
        .build()?)?;
    let inst = instrument(); let id = inst.id();
    engine.add_instrument(&inst)?;
    engine.add_strategy(Script { core: StrategyCore::new(StrategyConfig {
        strategy_id: Some(StrategyId::from("HISTORY-001")), order_id_tag: Some("001".into()),
        ..Default::default() }), id, scenario: scenario.into(), step: 0 })?;
    // Liquidation stress closes are the unchanged N1-02 oracle adverse prices (195/200/250).
    let stress = format!("{}.00", scenario.rsplit('_').next().unwrap_or_default());
    let prices = match scenario {
        "multi_cycle" => vec!["100.00", "110.00", "90.00", "120.00"],
        "reversal" => vec!["100.00", "110.00", "90.00"],
        s if s.starts_with("funding_") => vec!["100.00"; 4],
        s if s.starts_with("liquidation_") => vec!["100.00", stress.as_str(), stress.as_str()],
        _ => vec!["100.00", "105.00", "110.00"],
    };
    let mut data: Vec<Data> = prices.iter().enumerate().map(|(i, price)| {
        let ts = UnixNanos::from(1_800_000_000_000_000_000u64 + i as u64 * 1_000_000_000);
        Data::Quote(QuoteTick::new(id, Price::from(*price), Price::from(*price),
            Quantity::from("100.000"), Quantity::from("100.000"), ts, ts))
    }).collect();
    data.extend(funding_updates(scenario, id));
    engine.add_data(data, None, true, true)?;
    // Passive subscriber retains each native FundingSettlement as published. Not a BusTap: the bus has one
    // tap slot, and replacing it would disable native event-store capture.
    let settlements = Rc::new(RefCell::new(Vec::new()));
    let sink = settlements.clone();
    let topic = msgbus::switchboard::get_funding_settlement_topic(id);
    msgbus::subscribe_any(topic.as_str().into(), ShareableMessageHandler::from_typed(move |event: &FundingSettlement|
        sink.borrow_mut().push(serde_json::to_value(event).unwrap_or(Value::Null))), None);
    let run = engine.run(None, None, None, false);
    // N2-06 cases retain a native fail-closed run error for refusal tests; N2-05 cases still require success.
    let run_error = run.err().map(|e| format!("{e:#}"));
    ensure!(run_error.is_none() || scenario.starts_with("funding_") || scenario.starts_with("liquidation_"),
        "native run failed: {run_error:?}");
    let funding_settlements = settlements.borrow().clone();
    let state = observation(&engine.kernel().cache, &mut engine.kernel().portfolio.borrow_mut())?;
    // Exact native quote that priced the producer's portfolio, retained with its native encoding.
    let quote = engine.kernel().cache.borrow().quote(&id).copied()
        .ok_or_else(|| anyhow::anyhow!("producer quote absent"))?;
    let quote_native = serde_json::to_string(&quote)?;
    write(&root.join("native-position-witness.json"), &serde_json::to_value(
        engine.kernel().cache.borrow().positions(None,None,None,None,None).iter()
            .map(|p| serde_json::to_value(&**p)).collect::<std::result::Result<Vec<_>, _>>()?)?)?;
    write(&root.join("producer-state.json"), &json!({"pid": std::process::id(), "instance_id": instance.to_string(), "state": state}))?;
    let run_id = store.run_id().unwrap().to_string();
    ensure!(!store.is_halted(), "event store halted");
    // Fixed boundaries are truthful: after_seal is before Redis DB close, not in-flight seal.
    let mut lifecycle = Vec::new();
    boundary(root, "before_seal", &mut lifecycle)?;
    engine.kernel().exec_engine.borrow_mut().set_snapshot_anchorer(None);
    store.seal(UnixNanos::from(1_800_000_003_000_000_000u64));
    boundary(root, "after_seal", &mut lifecycle)?;
    engine.kernel().cache.borrow_mut().dispose(); // native DB close drains all queued Redis writes
    boundary(root, "after_drain", &mut lifecycle)?;
    let (manifest, reader) = open_event_store_replay_source(root.join("event_store"), &instance.to_string(), &run_id)?;
    ensure!(manifest.status == nautilus_event_store::RunStatus::Ended, "NATIVE_SEAL_FAILED");
    let watermark = reader.high_watermark()?;
    let plan = reader.snapshot_replay_plan()?;
    drop(reader);
    let chain = chain.lock().unwrap().clone();
    ensure!(chain.last() == plan.anchor.as_ref(), "NATIVE_ANCHOR_TAP_DIVERGED");
    let market_context = json!({"native": quote_native, "sha256": hash(quote_native.as_bytes()),
        "instrument_id": quote.instrument_id.to_string(), "ts_event": quote.ts_event.as_u64(),
        "source": {"pid": std::process::id(), "instance_id": instance.to_string(), "run_id": run_id}});
    lifecycle.push("acknowledged".into());
    write(&root.join("checkpoint.json"), &json!({"source": SOURCE, "binary_sha256": binary_hash()?,
        "cargo_lock_sha256": lock_hash(), "pid": std::process::id(), "instance_id": instance.to_string(),
        "trader": trader.to_string(), "run_id": run_id, "scenario": scenario, "state": state,
        "checkpoint": "NATIVE_SEALED_AND_CACHE_DATABASE_CLOSED", "resume": "RECONCILIATION_UNVERIFIED",
        "lifecycle": lifecycle, "watermark": watermark, "manifest": serde_json::to_value(manifest)?,
        "anchor": serde_json::to_value(plan.anchor)?, "anchor_chain": serde_json::to_value(&chain)?,
        "market_context": market_context, "run_error": run_error, "funding_settlements": funding_settlements,
        "redis_contents": redis_contents()?,
        "source_files": source_files(&root.join("event_store"))?}))?;
    lifecycle.pop();
    boundary(root, "acknowledged", &mut lifecycle)?;
    if hold { loop { std::thread::sleep(Duration::from_millis(100)); } }
    Ok(())
}

#[derive(Default)]
struct Traffic { publish: RefCell<Vec<String>>, send: RefCell<Vec<String>>, responses: RefCell<usize> }
impl BusTap for Traffic {
    fn on_publish(&self, topic: MStr<Topic>, _: &dyn Any) { self.publish.borrow_mut().push(topic.to_string()); }
    fn on_send(&self, endpoint: MStr<Endpoint>, _: &dyn Any) { self.send.borrow_mut().push(endpoint.to_string()); }
    fn on_response(&self, _: &UUID4, _: &dyn Any) { *self.responses.borrow_mut() += 1; }
}

fn restore(root: &Path, mode: &str) -> Result<&'static str> {
    let process_run = json!({"pid": std::process::id(), "process_run_id": UUID4::new().to_string(),
        "binary_sha256": binary_hash()?});
    write(&root.join("restore-process.json"), &process_run)?;
    let checkpoint_bytes = fs::read(root.join("checkpoint.json"))?;
    let trusted = std::env::var("CPW_EXPECTED_CHECKPOINT_SHA256")?;
    ensure!(trusted.len() == 64 && trusted == hash(&checkpoint_bytes), "UNVERIFIED_AUTHORITY_RECEIPT");
    let checkpoint: Value = serde_json::from_slice(&checkpoint_bytes)?;
    authority(&checkpoint)?;
    let contents = redis_contents()?;
    ensure!(contents == checkpoint["redis_contents"], "REDIS_PRODUCER_PAIR_MISMATCH");
    ensure!(source_files(&root.join("event_store"))? == checkpoint["source_files"], "EVENT_STORE_PRODUCER_PAIR_MISMATCH");
    let instance: UUID4 = checkpoint["instance_id"].as_str().unwrap().parse().map_err(anyhow::Error::msg)?;
    let trader = TraderId::new(checkpoint["trader"].as_str().unwrap());
    let rt = tokio::runtime::Runtime::new()?;
    let cache = Rc::new(RefCell::new(Cache::new(Some(config()), Some(db(&rt, trader, instance, true)?))));
    ensure!(checkpoint["checkpoint"] == "NATIVE_SEALED_AND_CACHE_DATABASE_CLOSED", "unsealed checkpoint");
    let mutable_before = json!({"orders": cache.borrow().orders(None,None,None,None,None).len(),
        "positions": cache.borrow().positions(None,None,None,None,None).len(),
        "accounts": cache.borrow().accounts_all_owned().len(),
        "archived": cache.borrow().position_snapshots(None,None).len()});
    ensure!(mutable_before.as_object().unwrap().values().all(|x| x == 0), "mutable preload");
    let traffic = Rc::new(Traffic::default());
    msgbus::set_bus_tap(traffic.clone());
    let run_id = checkpoint["run_id"].as_str().unwrap();
    let (manifest, reader) = open_event_store_replay_source(root.join("event_store"), &instance.to_string(), run_id)?;
    ensure!(manifest.binary_hash == binary_hash()? && manifest.crate_versions == lock_hash(), "native manifest identity mismatch");
    ensure!(manifest.status == nautilus_event_store::RunStatus::Ended, "UNSAFE_NATIVE_SEAL");
    ensure!(serde_json::to_value(&manifest)? == checkpoint["manifest"], "MANIFEST_IDENTITY_MISMATCH");
    ensure!(reader.high_watermark()? == checkpoint["watermark"].as_u64().unwrap(), "STALE_WATERMARK");
    let plan = reader.snapshot_replay_plan()?;
    ensure!(serde_json::to_value(&plan.anchor)? == checkpoint["anchor"], "ANCHOR_IDENTITY_MISMATCH");
    let mut payloads = BTreeMap::<String, usize>::new();
    let entries = reader.scan_range(1, reader.high_watermark()?, ScanDirection::Forward)
        .collect::<std::result::Result<Vec<_>, _>>()?;
    for entry in entries.iter().filter(|e| e.seq >= plan.from_seq) {
        *payloads.entry(entry.payload_type.to_string()).or_default() += 1;
    }
    // The pinned reader exposes only the latest native anchor; earlier anchors come from the
    // trusted producer receipt and must bind to the native log, Redis blob bytes and latest anchor.
    let chain = anchor_chain(&checkpoint, plan.anchor.as_ref(), reader.high_watermark()?)?;
    for anchor in &chain {
        ensure!(reader.scan_seq(anchor.high_watermark)?.is_some(), "ARCHIVE_CONTINUITY_BLOCKED: anchor watermark absent from native log");
        let blobs = contents.as_object().unwrap().iter()
            .filter(|(key, _)| key.ends_with(&format!(":general:{}", anchor.blob_ref))).collect::<Vec<_>>();
        ensure!(blobs.len() == 1, "ARCHIVE_CONTINUITY_BLOCKED: archived Redis blob absent or ambiguous");
        let blob = blobs[0].1["value"].as_str().unwrap_or_default();
        ensure!(compute_snapshot_content_hash(blob.as_bytes()) == anchor.content_hash, "ARCHIVE_CONTINUITY_BLOCKED: Redis frame overwritten");
    }
    // Open exposure needs the exact producer quote. No venue reconnect, flatten or resume follows.
    let quote = market_context(&checkpoint)?;
    let source_plan = json!({"run_id": run_id, "instance_id": instance.to_string(),
        "from_seq": plan.from_seq, "to_seq": plan.to_seq, "anchor": format!("{:?}", plan.anchor),
        "tail_payload_counts_inspected_only": payloads, "tail_replay_invoked": false,
        "manifest": serde_json::to_value(&manifest)?});
    write(&root.join("replay-contract.json"), &json!({"process": process_run,
        "mutable_before": mutable_before, "plan": source_plan}))?;
    // redb permits only one open handle per file, including read-only handles.
    drop(reader);
    if mode == "collision" {
        let entry = entries.iter().find(|e| e.payload_type.as_str() == "OrderFilled")
            .ok_or_else(|| anyhow::anyhow!("captured fill absent"))?.clone();
        let mut scratch_manifest = manifest.clone();
        scratch_manifest.run_id = "duplicate-sequence".into();
        scratch_manifest.high_watermark = 0;
        scratch_manifest.status = nautilus_event_store::RunStatus::Running;
        let mut backend = RedbBackend::new(root.join("collision"));
        backend.open_run(scratch_manifest)?;
        let captured_seq = entry.seq;
        let append = AppendEntry::without_indices(entry);
        // A real duplicate sequence is sent to the native backend; no CPW collision filter.
        let prefix = entries.iter().filter(|e| e.seq <= captured_seq).cloned()
            .map(AppendEntry::without_indices).collect::<Vec<_>>();
        let first = backend.append_batch(&prefix);
        let before = backend.high_watermark()?;
        let second = backend.append_batch(&[append]);
        let after = backend.high_watermark()?;
        let receipt = json!({"process": process_run, "captured_seq": captured_seq,
            "first_error": first.err().map(|e| e.to_string()), "duplicate_error": second.err().map(|e| e.to_string()),
            "high_watermark_before": before, "high_watermark_after": after});
        write(&root.join("collision-receipt.json"), &receipt)?;
        println!("{}", receipt);
        cache.borrow_mut().dispose();
        return Ok("COLLISION_PROBE_ONLY");
    }
    // Native current load and index build; no event-store tail application.
    let loaded = rt.block_on(cache.borrow_mut().cache_all());
    if loaded.is_ok() { cache.borrow_mut().build_index(); }
    let clock: Rc<RefCell<dyn Clock>> = Rc::new(RefCell::new(VirtualClock::new()));
    let mut portfolio = Portfolio::new(clock, cache.clone(), None);
    let current = observation(&cache, &mut portfolio)?;
    let current_equal = ["accounts", "orders", "positions", "fills"].iter()
        .all(|key| current[*key] == checkpoint["state"][*key]);
    let expected_frames = checkpoint["state"]["snapshots"].as_array().unwrap();
    let archive_contract = expected_frames.len() == chain.len() && chain.last() == plan.anchor.as_ref();
    // Prefix probes stop at these boundaries and close/drain in the common epilogue.
    let replay = loaded.and_then(|_| {
        ensure!(current_equal, "CURRENT_IDENTITY_MISMATCH");
        ensure!(archive_contract, "ARCHIVE_INDEX_CONTRACT_BLOCKED");
        if mode != "cache_only" {
            // Native fetch, BLAKE3 check and in-order frame restore for every archived cycle.
            for anchor in &chain { restore_cache_snapshot_blob(&mut cache.borrow_mut(), Some(anchor))?; }
            if let Some(quote) = quote.clone() { cache.borrow_mut().add_quote(quote)?; }
        }
        Ok(())
    });
    let archive_state = observation(&cache, &mut portfolio)?;
    if replay.is_ok() && !["cache_only", "archive_only"].contains(&mode) {
        portfolio.initialize_orders(); portfolio.initialize_positions();
    }
    let state = observation(&cache, &mut portfolio)?;
    let mut duplicate_receipt = Value::Null;
    if mode == "duplicate" && replay.is_ok() && state == checkpoint["state"] {
        // The native order cache contains the engine-associated event, unlike the pre-engine tap.
        let fill = state["fills"].as_array().unwrap().iter().rev().find(|f|
            !f["payload"]["position_id"].is_null() && state["positions"].as_array().unwrap().iter().any(|p|
                p["id"] == f["payload"]["position_id"] && p["trades"].as_array().unwrap().contains(&f["trade_id"])))
            .ok_or_else(|| anyhow::anyhow!("NATIVE_ASSOCIATION_BLOCKED"))?;
        let position_id = fill["payload"]["position_id"].as_str().unwrap();
        ensure!(state["positions"].as_array().unwrap().iter().any(|p| p["id"] == position_id
            && p["trades"].as_array().unwrap().contains(&fill["trade_id"])), "NATIVE_ASSOCIATION_BLOCKED: position/trade absent");
        let associated: OrderFilled = serde_json::from_value(fill["payload"].clone())?;
        let mut original = associated.clone();
        original.position_id = None; // Native pre-engine capture precedes association.
        let original_bytes = encode_order_filled(&original)?.payload;
        let mut envelope = entries.iter().find(|entry| entry.payload_type.as_str() == "OrderFilled"
            && entry.payload == original_bytes)
            .ok_or_else(|| anyhow::anyhow!("FIXTURE_CAPTURE_CORRELATION_ERROR"))?.clone();
        fs::write(root.join("captured-fill-payload.msgpack"), &envelope.payload)?;
        let associated_bytes = serde_json::to_vec(&fill["payload"])?;
        fs::write(root.join("associated-fill-payload.json"), &associated_bytes)?;
        let mut attempts = Vec::new();
        for conflict in [false, false, true] {
            let mut payload = fill["payload"].clone();
            if conflict { payload["last_qty"] = json!("9.000"); }
            let native_fill: OrderFilled = serde_json::from_value(payload.clone())?;
            envelope.payload = encode_order_filled(&native_fill)?.payload;
            fs::write(root.join(if conflict { "conflicting-fill.msgpack" } else { "associated-fill.msgpack" }), &envelope.payload)?;
            envelope.entry_hash = envelope.recompute_hash();
            let applied = apply_cache_replay_entry(&mut cache.borrow_mut(), &envelope);
            portfolio.initialize_orders(); portfolio.initialize_positions();
            let after = observation(&cache, &mut portfolio)?;
            attempts.push(json!({"conflict": conflict, "payload": payload,
                "native_error": applied.err().map(|x| x.to_string()), "state_after": after,
                "unchanged": state == after}));
        }
        duplicate_receipt = json!({"position_id": position_id, "native_fill": fill,
            "associated_payload_sha256": hash(&associated_bytes), "attempts": attempts,
            "unchanged": attempts.iter().all(|a| a["unchanged"] == true)});
    }
    let receipt = json!({"process": process_run, "source": source_plan, "mutable_before": mutable_before,
        "state": state, "native_error": replay.as_ref().err().map(|x| x.to_string()),
        "current_state": current, "current_equal": current_equal, "archive_state": archive_state,
        "archive_contract": archive_contract, "tail_replay_invoked": false, "mode": mode,
        "bus_publishes": traffic.publish.borrow().clone(), "bus_sends": traffic.send.borrow().clone(),
        "bus_responses": *traffic.responses.borrow(),
        "registered_endpoints": msgbus::get_message_bus().borrow().endpoints().iter().map(|s| s.to_string()).collect::<Vec<_>>(),
        "duplicate": duplicate_receipt, "resume": "VENUE_RECONCILIATION_REQUIRED / NO_NEW_ORDERS / NO_RESUME",
        "anchor_chain": serde_json::to_value(&chain)?, "market_context_applied": quote.is_some(),
        "restored_mark": cache.borrow().quote(&instrument().id()).map(serde_json::to_value).transpose()?,
        "equal": state == checkpoint["state"]});
    write(&root.join("restore-receipt.json"), &receipt)?;
    println!("{}", receipt);
    cache.borrow_mut().dispose();
    msgbus::clear_bus_tap();
    ensure!(replay.is_ok(), "NATIVE_CURRENT_ARCHIVE_ERROR");
    ensure!(mode == "cache_only" || state == checkpoint["state"], "RECOVERY_NOT_QUALIFIED");
    ensure!(mode != "duplicate" || duplicate_receipt["unchanged"] == true, "DUPLICATE_FILL_MUTATED_STATE");
    ensure!(redis_contents()? == checkpoint["redis_contents"], "RESTORE_ECONOMIC_WRITE");
    ensure!(source_files(&root.join("event_store"))? == checkpoint["source_files"], "RESTORE_EVENT_STORE_WRITE");
    // A reconstructed open position is diagnostic state only; any future activation needs venue reconciliation.
    Ok(if quote.is_some() { "OPEN_EXPOSURE_RECONSTRUCTED_NO_RESUME" } else { "RECOVERY_ADMITTED_SEALED" })
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().collect();
    ensure!(args.len() >= 3, "produce|hold|restore DIRECTORY [round_trip|reversal]");
    let root = Path::new(&args[2]);
    match args[1].as_str() {
        "resume" => anyhow::bail!("RECONCILIATION_UNVERIFIED / NO_NEW_ORDERS"),
        "restore" | "duplicate" => {
            let result = restore(root, &args[1]);
            let receipt = json!({"pid": std::process::id(), "binary_sha256": binary_hash()?,
                "decision": result.as_ref().map_or("RECONCILIATION_REQUIRED", |d| *d),
                "error": result.as_ref().err().map(|e| format!("{e:#}")),
                "order_authority": "NO_NEW_ORDERS / NO_RESUME",
                "venue_reconciliation_required_before_activation": true});
            write(&root.join("admission.json"), &receipt)?;
            result.map(|_| ())
        },
        "produce" | "hold" => { ensure!(args.len() == 4 && SCENARIOS.contains(&args[3].as_str()), "scenario");
            produce(root, &args[3], args[1] == "hold") },
        _ => anyhow::bail!("RECONCILIATION_REQUIRED / unsupported diagnostic mode / NO_NEW_ORDERS"),
    }
}

#[cfg(test)]
mod admission_tests {
    use super::*;

    fn receipt() -> Value {
        json!({"source": SOURCE, "binary_sha256": binary_hash().unwrap(), "cargo_lock_sha256": lock_hash(),
            "checkpoint": "NATIVE_SEALED_AND_CACHE_DATABASE_CLOSED", "pid": 123,
            "lifecycle": ["before_seal", "after_seal", "after_drain", "acknowledged"],
            "trader": "fixture", "instance_id": UUID4::new().to_string(), "run_id": "fixture-run", "watermark": 24,
            "redis_contents": {"key": "value"}, "source_files": {"source.redb": "hash"}, "manifest": {"status": "Ended"},
            "state": {"fills": [{"order_id": "order-1", "trade_id": "trade-1"}]}})
    }

    #[test]
    fn complete_receipt_passes_authority_shape() { assert!(authority(&receipt()).is_ok()); }

    #[test]
    fn untrusted_identity_and_incomplete_receipts_refuse() {
        for field in ["source", "binary_sha256", "cargo_lock_sha256", "checkpoint", "pid", "lifecycle",
            "trader", "instance_id", "run_id", "watermark", "redis_contents", "source_files", "manifest", "state"] {
            let mut cp = receipt();
            cp.as_object_mut().unwrap().remove(field);
            assert!(authority(&cp).is_err(), "missing {field}");
        }
    }

    #[test]
    fn failed_native_run_refuses() {
        let mut cp = receipt(); cp["run_error"] = json!("Late funding boundary");
        assert!(authority(&cp).unwrap_err().to_string().contains("NATIVE_RUN_FAILED"));
    }

    #[test]
    fn stale_watermark_and_repeated_trade_refuse() {
        let mut cp = receipt(); cp["watermark"] = json!(0);
        assert!(authority(&cp).is_err());
        cp = receipt();
        cp["state"]["fills"] = json!([{"order_id": "o", "trade_id": "t"}, {"order_id": "o", "trade_id": "t", "qty": "9"}]);
        assert!(authority(&cp).unwrap_err().to_string().contains("CONFLICTING_FILL"));
    }

    fn archived(frames: &[&[u8]]) -> (Value, Vec<SnapshotAnchor>) {
        let position = "BTCUSDT-PERP.SIM-HISTORY-001";
        let mut rows = Vec::new();
        let mut chain = Vec::new();
        for (index, bytes) in frames.iter().enumerate() {
            rows.push(json!({"position_id": position, "index": index, "sha256": hash(bytes), "bytes": bytes.to_vec()}));
            chain.push(SnapshotAnchor::new(10 * (index as u64 + 1),
                format!("cache://position-snapshots/{position}/{index}"), compute_snapshot_content_hash(bytes)));
        }
        let mut cp = receipt();
        cp["state"]["snapshots"] = json!(rows);
        cp["anchor_chain"] = serde_json::to_value(&chain).unwrap();
        (cp, chain)
    }

    #[test]
    fn complete_native_anchor_chain_passes() {
        let (cp, chain) = archived(&[b"cycle-0", b"cycle-1"]);
        assert_eq!(anchor_chain(&cp, chain.last(), 30).unwrap(), chain);
    }

    #[test]
    fn missing_reordered_stale_altered_or_unbound_anchors_refuse() {
        let (base, chain) = archived(&[b"cycle-0", b"cycle-1"]);
        let mut faults = Vec::new();
        let mut cp = base.clone(); cp["anchor_chain"].as_array_mut().unwrap().remove(0); faults.push(cp);
        let mut cp = base.clone(); cp["anchor_chain"].as_array_mut().unwrap().swap(0, 1); faults.push(cp);
        let mut cp = base.clone(); cp["anchor_chain"][0]["high_watermark"] = json!(25); faults.push(cp);
        let mut cp = base.clone(); cp["anchor_chain"][0]["content_hash"] = json!("blake3:00"); faults.push(cp);
        let mut cp = base.clone(); cp["state"]["snapshots"][0]["bytes"] = json!(b"cycle-1".to_vec()); faults.push(cp);
        let mut cp = base.clone(); cp.as_object_mut().unwrap().remove("anchor_chain"); faults.push(cp);
        for cp in &faults {
            assert!(anchor_chain(cp, chain.last(), 30).unwrap_err().to_string().contains("ARCHIVE_CONTINUITY_BLOCKED"));
        }
        // Not ending at the native latest anchor, or past the durable watermark, also refuses.
        assert!(anchor_chain(&base, chain.first(), 30).is_err());
        assert!(anchor_chain(&base, None, 30).is_err());
        assert!(anchor_chain(&base, chain.last(), 15).is_err());
    }

    fn open_receipt() -> Value {
        let quote = QuoteTick::new(InstrumentId::from("BTCUSDT-PERP.SIM"), Price::from("110.00"), Price::from("110.00"),
            Quantity::from("100.000"), Quantity::from("100.000"), UnixNanos::from(30), UnixNanos::from(30));
        let native = serde_json::to_string(&quote).unwrap();
        let mut cp = receipt();
        cp["manifest"]["end_ts_init"] = json!(40);
        cp["state"]["positions"] = json!([{"closed": false, "native": {"instrument_id": "BTCUSDT-PERP.SIM", "ts_last": 10}}]);
        cp["market_context"] = json!({"native": native, "sha256": hash(native.as_bytes()),
            "instrument_id": "BTCUSDT-PERP.SIM", "ts_event": 30,
            "source": {"pid": cp["pid"], "instance_id": cp["instance_id"], "run_id": cp["run_id"]}});
        cp
    }

    #[test]
    fn exact_producer_quote_prices_open_exposure() {
        let quote = market_context(&open_receipt()).unwrap().unwrap();
        assert_eq!(quote.bid_price, Price::from("110.00"));
        let mut closed = open_receipt(); closed["state"]["positions"][0]["closed"] = json!(true);
        assert!(market_context(&closed).unwrap().is_none());
    }

    #[test]
    fn missing_stale_wrong_or_cross_paired_quotes_refuse() {
        let mut faults = Vec::new();
        let mut cp = open_receipt(); cp.as_object_mut().unwrap().remove("market_context"); faults.push(cp);
        let mut cp = open_receipt(); cp["market_context"]["sha256"] = json!("0"); faults.push(cp);
        let mut cp = open_receipt(); cp["market_context"]["source"]["run_id"] = json!("other-run"); faults.push(cp);
        let mut cp = open_receipt(); cp["market_context"]["ts_event"] = json!(31); faults.push(cp);
        let mut cp = open_receipt(); cp["state"]["positions"][0]["native"]["ts_last"] = json!(35); faults.push(cp);
        let mut cp = open_receipt(); cp["state"]["positions"][0]["native"]["instrument_id"] = json!("ETHUSDT-PERP.SIM"); faults.push(cp);
        let mut cp = open_receipt(); cp["manifest"]["end_ts_init"] = json!(20); faults.push(cp);
        for cp in &faults {
            assert!(market_context(cp).unwrap_err().to_string().contains("OPEN_EXPOSURE_REQUIRES_RECONCILIATION"));
        }
    }

    #[test]
    fn approximate_position_metrics_are_not_exact_decimal_evidence() {
        let value = json!({"realized_return": 0.18181818181818182_f64});
        let parsed: Value = serde_json::from_slice(&serde_json::to_vec(&value).unwrap()).unwrap();
        assert_ne!(value, parsed, "frozen default serde float parser diagnostic");
    }
}
