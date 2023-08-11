Main.py is the code for my backend of my To-do-list application and right now you can create new notes and they will be saved in MongoDB, you can also get all of the notes with all of thier inflo including the _id which right now i am trying to use in order to update a note but it does not work. In the future you should be able to create update delete and search for notes in my React app where the front end is located.

Installation for backend: fastapi, uvicorn, pymongo, poetry ...
Installation for frontend: npm, react-app...

Commands for backend: poetry shell -> uvicorn main:app --reload
Commands for frontend: npm start
Possible commands for MongoDB; mongosh, mongod 