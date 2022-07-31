pyinstaller --clean -F -c -i PyDeck.ico -n PyDeck src\main.py
copy /y PyDeck.stpl dist\
copy /y PyDeck.yaml dist\
copy /y PyDeck.yaml.schema dist\
xcopy /y icon\* dist\icon\