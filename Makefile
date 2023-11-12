init:
	python3 -m pip install -r requirements.txt
executable:
	pyinstaller -F conquers.py
doc:
	cd docs && make clean
	sphinx-apidoc -o docs/source . "conquers.py"
	cd docs && make html
	cp -r docs/build/html/. docs/
