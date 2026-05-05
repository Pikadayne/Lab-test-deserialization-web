from app import app


for rule in sorted(app.url_map.iter_rules(), key=lambda item: item.rule):
    methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
    print(f"{methods:12} {rule.rule} -> {rule.endpoint}")
