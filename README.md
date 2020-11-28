# FlaskFire + realtime chat
Me trying to build a realtime chat system using firebase and flask. 

![flaskfiress](https://user-images.githubusercontent.com/19330397/100495163-9d4a7c00-316e-11eb-9a25-78505c368522.PNG)




### Thing I know:
* I can use document snapchat feature to get changes in documents
* I can use socketIO to send,recive data between the server and the client. realtime.

### Current Status:
* ~~One user can use the system realtime. But when more than one dosen't work due to `chat` variable~~
* Desinged as mentioned the image and manage to work all!

### ToDo
* ~~Find a way to change session variables when within the `on_snapshot()` method.~~
* ~~No need to use sessions. Created a socketIo event in client to listen on chatid and send `True` if there are any changes to required clients.~~
* Add more features to core

### Added features
* Desktop notification when chat is not focused
* emojis
