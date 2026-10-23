//! Private offline route fixture. Native engines own every economic and replay operation.
use std::{any::Any, cell::RefCell, collections::BTreeMap, fmt, fs, path::Path, rc::Rc, time::Duration};
use anyhow::{Result, ensure};
use nautilus_backtest::{config::{BacktestEngineConfig, SimulatedVenueConfig}, engine::BacktestEngine};
use nautilus_common::{cache::{Cache, CacheConfig}, cache::database::CacheDatabaseFactory,
    clock::{Clock, VirtualClock}, enums::Environment, actor::DataActor,
    msgbus::{self, BusTap, MStr, Topic, Endpoint}};
use nautilus_core::{UUID4, UnixNanos};
use nautilus_event_store::{EventStoreLifecycle, ScanDirection, apply_cache_replay_entry,
    open_event_store_replay_source, restore_cache_snapshot_blob};
use nautilus_event_store::backend::{AppendEntry, EventStore, RedbBackend};
use nautilus_execution::models::fee::{FeeModelAny, MakerTakerFeeModel};
use nautilus_infrastructure::redis::cache::RedisCacheConfig;
use nautilus_model::{accounts::Account, data::{Data, QuoteTick}, enums::{AccountType, BookType, OmsType, OrderSide},
    identifiers::{InstrumentId, StrategyId, Symbol, TraderId, Venue},
    instruments::{CryptoPerpetual, Instrument, InstrumentAny}, orders::Order, events::OrderEventAny,
    types::{Currency, Money, Price, Quantity}};
use nautilus_portfolio::Portfolio;
use nautilus_system::{RegisteredComponents, event_store::{EventStoreConfig, RunIdentity}};
use nautilus_trading::{Strategy, StrategyConfig, StrategyCore, nautilus_strategy};
use rust_decimal::Decimal;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const SOURCE: &str = "55c0e82053142bce3a5cba4de4221d3929c2d3bc";
fn hash(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
fn binary_hash() -> Result<String> { Ok(hash(&fs::read(std::env::current_exe()?)?)) }
fn lock_hash() -> String { hash(include_bytes!("../Cargo.lock")) }
fn write(path: &Path, value: &Value) -> Result<()> { fs::write(path, serde_json::to_vec_pretty(value)?)?; Ok(()) }
fn instrument() -> InstrumentAny {
    CryptoPerpetual::builder().instrument_id(InstrumentId::from("BTCUSDT-PERP.SIM"))
        .raw_symbol(Symbol::from("BTCUSDT"))
        .base_currency(Currency::BTC()).quote_currency(Currency::USDT()).settlement_currency(Currency::USDT())
        .is_inverse(false).price_precision(2).size_precision(3)
        .price_increment(Price::from("0.01")).size_increment(Quantity::from("0.001"))
        .margin_init(Decimal::new(1, 1)).margin_maint(Decimal::new(5, 2))
        .ts_event(UnixNanos::default()).ts_init(UnixNanos::default()).build().unwrap().into()
}
fn config() -> CacheConfig { CacheConfig { use_trader_prefix: true, use_instance_id: false,
    flush_on_start: false, buffer_interval_ms: Some(0), ..Default::default() } }
fn db(rt: &tokio::runtime::Runtime, trader: TraderId, instance: UUID4)
    -> Result<Box<dyn nautilus_common::cache::database::CacheDatabaseAdapter>> {
    let port = std::env::var("CPW_ROUTE_REDIS_PORT").unwrap_or_else(|_| "6397".into()).parse::<u16>()?;
    ensure!([6397, 6398].contains(&port), "only owned fixture Redis ports permitted");
    let redis = RedisCacheConfig { host: Some("127.0.0.1".into()), port: Some(port),
        number_of_retries: 0, connection_timeout: 2, response_timeout: 2, ..Default::default() };
    rt.block_on(redis.create(trader, instance, config()))
}

struct Script { core: StrategyCore, id: InstrumentId, reversal: bool, step: usize }
nautilus_strategy!(Script);
impl fmt::Debug for Script {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { f.debug_struct("Script").finish() }
}
impl DataActor for Script {
    fn on_start(&mut self) -> Result<()> { self.subscribe_quotes(self.id, None, None); Ok(()) }
    fn on_quote(&mut self, _: &QuoteTick) -> Result<()> {
        let action = if self.reversal { [(OrderSide::Buy, "1.000"), (OrderSide::Sell, "2.000"),
            (OrderSide::Buy, "1.000")] } else { [(OrderSide::Buy, "1.000"),
            (OrderSide::Sell, "0.000"), (OrderSide::Sell, "1.000")] };
        if self.step < 3 {
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
    let cache = cache.borrow();
    let positions = cache.positions(None, None, None, None, None);
    let orders = cache.orders(None, None, None, None, None);
    let mut snapshots = Vec::new();
    let mut position_rows = Vec::new();
    for position in positions {
        let bytes = cache.position_snapshot_bytes(&position.id).unwrap_or_default();
        for frame in bytes { snapshots.push(json!({"position_id": position.id.to_string(), "sha256": hash(&frame), "bytes": frame})); }
        position_rows.push(json!({"id": position.id.to_string(), "closed": position.is_closed(),
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
    let account_rows = accounts.iter().map(|account| json!({"id": account.id().to_string(),
        "equity": account.balance_total(Some(Currency::USDT())).map(|x| x.as_decimal().to_string())})).collect::<Vec<_>>();
    Ok(json!({"portfolio_realized_pnl": pnl, "positions": position_rows, "orders": order_rows,
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
    engine.kernel().cache.borrow_mut().set_database(db(&rt, trader, instance)?);
    let clock = engine.kernel().clock.clone();
    let identity = RunIdentity { binary_hash: binary_hash()?, schema_version: 1,
        crate_versions: lock_hash(), config_hash: hash(scenario.as_bytes()),
        feature_flags: vec![SOURCE.into()], ..Default::default() };
    let mut store = EventStoreLifecycle::boot(Some(EventStoreConfig {
        base_dir: root.join("event_store"), identity, ..Default::default() }), instance, clock)?;
    store.open(instance, &RegisteredComponents::default(), Environment::Backtest)?;
    engine.kernel().exec_engine.borrow_mut().set_snapshot_anchorer(store.snapshot_anchorer());
    engine.add_venue(SimulatedVenueConfig::builder().venue(Venue::from("SIM"))
        .oms_type(OmsType::Netting).account_type(AccountType::Margin).book_type(BookType::L1_MBP)
        .starting_balances(vec![Money::from("10000 USDT")])
        .base_currency(Currency::USDT()).default_leverage(Decimal::ONE)
        .fee_model(FeeModelAny::MakerTaker(MakerTakerFeeModel::new(Decimal::new(4, 4), Decimal::new(4, 4))).into())
        .build()?)?;
    let inst = instrument(); let id = inst.id();
    engine.add_instrument(&inst)?;
    engine.add_strategy(Script { core: StrategyCore::new(StrategyConfig {
        strategy_id: Some(StrategyId::from("HISTORY-001")), order_id_tag: Some("001".into()),
        ..Default::default() }), id, reversal: scenario == "reversal", step: 0 })?;
    let prices = if scenario == "reversal" { ["100.00", "110.00", "90.00"] } else { ["100.00", "105.00", "110.00"] };
    let quotes = prices.iter().enumerate().map(|(i, price)| {
        let ts = UnixNanos::from(1_800_000_000_000_000_000u64 + i as u64 * 1_000_000_000);
        Data::Quote(QuoteTick::new(id, Price::from(*price), Price::from(*price),
            Quantity::from("100.000"), Quantity::from("100.000"), ts, ts))
    }).collect();
    engine.add_data(quotes, None, true, true)?;
    engine.run(None, None, None, false)?;
    let state = observation(&engine.kernel().cache, &mut engine.kernel().portfolio.borrow_mut())?;
    let run_id = store.run_id().unwrap().to_string();
    ensure!(!store.is_halted(), "event store halted");
    // Native close waits for writer acknowledgement. The crash is after this fully sealed checkpoint.
    engine.kernel().exec_engine.borrow_mut().set_snapshot_anchorer(None);
    store.seal(UnixNanos::from(1_800_000_003_000_000_000u64));
    engine.kernel().cache.borrow_mut().dispose(); // native DB close drains all queued Redis writes
    write(&root.join("checkpoint.json"), &json!({"source": SOURCE, "binary_sha256": binary_hash()?,
        "cargo_lock_sha256": lock_hash(), "pid": std::process::id(), "instance_id": instance.to_string(),
        "trader": trader.to_string(), "run_id": run_id, "scenario": scenario, "state": state,
        "checkpoint": "NATIVE_SEALED_AND_CACHE_DATABASE_CLOSED", "resume": "RECONCILIATION_UNVERIFIED"}))?;
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

fn restore(root: &Path, mode: &str) -> Result<()> {
    let process_run = json!({"pid": std::process::id(), "process_run_id": UUID4::new().to_string(),
        "binary_sha256": binary_hash()?});
    write(&root.join("restore-process.json"), &process_run)?;
    let checkpoint: Value = serde_json::from_slice(&fs::read(root.join("checkpoint.json"))?)?;
    ensure!(checkpoint["source"] == SOURCE, "wrong source identity");
    ensure!(checkpoint["binary_sha256"] == binary_hash()?, "wrong native binary identity");
    ensure!(checkpoint["cargo_lock_sha256"] == lock_hash(), "wrong dependency identity");
    let instance: UUID4 = checkpoint["instance_id"].as_str().unwrap().parse().map_err(anyhow::Error::msg)?;
    let trader = TraderId::new(checkpoint["trader"].as_str().unwrap());
    let rt = tokio::runtime::Runtime::new()?;
    let cache = Rc::new(RefCell::new(Cache::new(Some(config()), Some(db(&rt, trader, instance)?))));
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
    let plan = reader.snapshot_replay_plan()?;
    let mut payloads = BTreeMap::<String, usize>::new();
    let entries = reader.scan_range(1, reader.high_watermark()?, ScanDirection::Forward)
        .collect::<std::result::Result<Vec<_>, _>>()?;
    for entry in entries.iter().filter(|e| e.seq >= plan.from_seq) {
        *payloads.entry(entry.payload_type.to_string()).or_default() += 1;
    }
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
        return Ok(());
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
    let archive_contract = if checkpoint["scenario"] == "reversal" {
        expected_frames.len() == 1 && plan.anchor.as_ref().is_some_and(|a| a.blob_ref.ends_with("/0"))
    } else { expected_frames.is_empty() && plan.anchor.is_none() };
    // Prefix probes stop at these boundaries and close/drain in the common epilogue.
    let replay = loaded.and_then(|_| {
        ensure!(current_equal, "CURRENT_IDENTITY_MISMATCH");
        ensure!(archive_contract, "ARCHIVE_INDEX_CONTRACT_BLOCKED");
        if mode != "cache_only" {
            restore_cache_snapshot_blob(&mut cache.borrow_mut(), plan.anchor.as_ref())?;
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
        let fill = entries.iter().rev().find(|entry| entry.payload_type.as_str() == "OrderFilled")
            .ok_or_else(|| anyhow::anyhow!("no genuine captured fill for duplicate control"))?;
        let applied = apply_cache_replay_entry(&mut cache.borrow_mut(), fill);
        let after = observation(&cache, &mut portfolio)?;
        duplicate_receipt = json!({"native_error": applied.err().map(|x| x.to_string()),
            "state_before": state, "state_after": after, "unchanged": state == after});
    }
    let receipt = json!({"process": process_run, "source": source_plan, "mutable_before": mutable_before,
        "state": state, "native_error": replay.as_ref().err().map(|x| x.to_string()),
        "current_state": current, "current_equal": current_equal, "archive_state": archive_state,
        "archive_contract": archive_contract, "tail_replay_invoked": false, "mode": mode,
        "bus_publishes": traffic.publish.borrow().clone(), "bus_sends": traffic.send.borrow().clone(),
        "bus_responses": *traffic.responses.borrow(),
        "registered_endpoints": msgbus::get_message_bus().borrow().endpoints().iter().map(|s| s.to_string()).collect::<Vec<_>>(),
        "duplicate": duplicate_receipt, "resume": "RECONCILIATION_UNVERIFIED / NO_NEW_ORDERS",
        "equal": state == checkpoint["state"]});
    write(&root.join("restore-receipt.json"), &receipt)?;
    println!("{}", receipt);
    cache.borrow_mut().dispose();
    msgbus::clear_bus_tap();
    ensure!(replay.is_ok(), "NATIVE_CURRENT_ARCHIVE_ERROR");
    ensure!(mode == "cache_only" || state == checkpoint["state"], "RECOVERY_NOT_QUALIFIED");
    ensure!(mode != "duplicate" || duplicate_receipt["unchanged"] == true, "DUPLICATE_FILL_MUTATED_STATE");
    Ok(())
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().collect();
    ensure!(args.len() >= 3, "produce|hold|restore DIRECTORY [round_trip|reversal]");
    let root = Path::new(&args[2]);
    match args[1].as_str() {
        "resume" => anyhow::bail!("RECONCILIATION_UNVERIFIED / NO_NEW_ORDERS"),
        "restore" | "cache_only" | "archive_only" | "duplicate" | "collision" => restore(root, &args[1]),
        "produce" | "hold" => { ensure!(args.len() == 4 && ["round_trip", "reversal"].contains(&args[3].as_str()), "scenario");
            produce(root, &args[3], args[1] == "hold") },
        _ => anyhow::bail!("unsupported mode"),
    }
}
