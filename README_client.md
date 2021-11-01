# Client Description

The client, which is the game-playing bot, was written in Python and connects to the game server over tcp sockets. It is able to beat a random player at a high rate, even when given the second move of the game. Read below for directions on how to invoke it in tandem with the game server. 


## Usage

After cloning the repository, you will need to start the game server. Instructions are found in README_server.md. To start the client and establish a connection to the server, first navigate to **/sdks/python** and run the following command on a terminal:
python client.py `<depth>` `(optional) <port>` `(optional) <host>`
  * `<depth>` is an integer which specifies how many moves ahead in the game tree the bot should look
  * `<port>` is an optional integer argument to specify which port will be used to connect to the server. 1337 by default.
  * `<host>` is an optional string argument to specify the IP address of the host. Address of local system by default.


## Additional Notes

* Make sure to specify the same port at which the server is listening for a player if necessary. The server's default for P1 is 1337 and P2 is 1338.
* Against a random player, it is best to set depth to 0. The more advanced the opponent, the higher this parameter should be.
* For testing purposes, client_easy_opp.py is provided as a short-sighted, basic opponent which chooses the play which flips the most pieces every time. Invoked identically to original client.py but without the `<depth>` parameter.
