# Benchmarking-UDP-protocol-and-its-inner-workings-ARQ-UDP-

In this project, I implemented Automatic Repeat Request Algorithms using Python UDP protocol (networking). </br>
Specifically, the Go Back N and Selective Repeat Algorithm. </br>
I made slight changes to the Selective Repeat Algorithm using a Red Black Tree as well as Double Linked List in order to speed things up.

Additionally, I benchmarked parameters such as MTU (Max Transmission Unit/Size in a packet), Compression, Number of Threads dedicated to running the UDP.

# Unfortunately, the powerpoint slides I used for presenting is lost as my school closed the Google Drive Share.

Nonetheless, here are some plots that I happened to upload to this Github.

Go Back N: Experiments found that this is the slowest of all Algorithms that I Implemented. This is to be expected. 
Plot below shows the send vs receive time for each packet.
![image](https://user-images.githubusercontent.com/54625060/182522180-c3f13a4e-3340-44fa-8c2d-d58737309fef.png)
</br>

Selective Repeat, with Data Structure changed to Red Black Tree: 
This is the fastest out of all the algorithms I implemented
![image](https://user-images.githubusercontent.com/54625060/182522339-e07ed486-d366-4999-b2d2-20f291d34fe0.png)
</br>

Selective Repeat, with Data Structure changed to doubly linked list:
Second fastest
![image](https://user-images.githubusercontent.com/54625060/182522384-bafcf670-711e-42a5-830a-bf51f4879a24.png)
</br> 
