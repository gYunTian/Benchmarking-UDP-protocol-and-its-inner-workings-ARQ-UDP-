# Benchmarking-UDP-protocol-and-its-inner-workings-ARQ-UDP-

Inspired by Google's QUIC, In this project, I implemented <b>Automatic Repeat Request Algorithms using Python UDP protocol (networking)</b>. </br></br>
Specifically, the <b> Go Back N and Selective Repeat Algorithm</b>. </br></br>
I made slight changes to the Selective Repeat Algorithm using a Red Black Tree as well as Double Linked List in order to speed things up.

Additionally, I <b>benchmarked parameters such as MTU (Max Transmission Unit/Size in a packet), Compression, Number of Threads dedicated to running the UDP</b>.

# Why is this important
Getting into the <b>inner workings of a network protocol allows us to better understand what are the trade offs between the parameters</b>

1) Say if one wants to implement a custom application, one can implement certain feature of the network protocol to behave in specific ways beneficial to the underlying app, </br> 
2) i.e. we can include logging of the packets, failure rate, time taken (round time), increase number of threads, custom data structures/packet format and for security purposes (as the code are written by oneself)


# Unfortunately, the powerpoint slides I used for presenting is lost as my school closed the Google Drive Share.

Nonetheless, here are some plots that I happened to upload to this Github.

<b> Go Back N: Experiments found that this is the slowest of all Algorithms </b> that I Implemented. 
This is to be expected. 
Plot below shows the send vs receive time for each packet.</br></br>

![image](https://user-images.githubusercontent.com/54625060/182522180-c3f13a4e-3340-44fa-8c2d-d58737309fef.png)
</br>

<b> Selective Repeat, with Data Structure changed to Red Black Tree</b>: 
This is the fastest out of all the algorithms I implemented. The Blue lines indicate that a large amount of packets were sent in a short period of time thereby leading to a faster overall speed.
![image](https://user-images.githubusercontent.com/54625060/182522339-e07ed486-d366-4999-b2d2-20f291d34fe0.png)
</br>

<b>Selective Repeat, with Data Structure changed to doubly linked list</b>:
Second fastest among the 3. A more well behaved algorithm with lesser amount of packets sent in any period of time and but still fast enough.
![image](https://user-images.githubusercontent.com/54625060/182522384-bafcf670-711e-42a5-830a-bf51f4879a24.png)
</br> 
