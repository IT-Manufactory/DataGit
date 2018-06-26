install:
		(\
            virtualenv -p python3 venv;\
  			source venv/bin/activate;\
  			pip3 install -r requirements.txt;\
		)

wininstall:
		(\
            virtualenv -p python venv;\
  			source venv/Scripts/activate;\
  			pip install -r requirements.txt;\
		)

run :
	(\
        source venv/bin/activate;\
        cd mac;\
        python3 run.py;\
        deactivate;\
	)
winrun :
	(\
        source venv/Scripts/activate;\
        cd windows;\
        python run.py;\
        deactivate;\
	)
