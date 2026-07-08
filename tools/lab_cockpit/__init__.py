"""Static, read-only lab product cockpit.

A product-grade operator cockpit that projects committed lab evidence — the
merged coordinator state model and the concluded real-traffic four-hypothesis
batch — into a single deterministic static page. It is visualization only: it
runs no strategy, fetches no data, executes no transition, and renders no
run / approve / promote / retry / scheduler control.

Public entry point: :func:`tools.lab_cockpit.model.build_cockpit_data`.
"""
