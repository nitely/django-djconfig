clean:
	rm -fr dist/ doc/_build/ *.egg-info/

docs:
	cd docs && make clean && make html

test:
	python -Wall runtests.py

sdist: test clean
	python setup.py sdist

release: test clean
	python setup.py sdist && twine check dist/* && twine upload dist/*

.PHONY: clean docs test sdist release
