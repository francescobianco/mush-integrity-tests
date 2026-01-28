
push:
	@git add .
	@git commit -am "Update at $$(date)" || true
	@git push