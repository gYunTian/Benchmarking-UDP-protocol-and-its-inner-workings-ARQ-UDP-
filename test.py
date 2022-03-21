        # saved = LAST_ACK + 1
        # curr = LAST_ACK + IN_TRANSIT + 1
        # timer = time.time()
        # heur = AVG_RTT+AVG_RTT+AVG_RTT+0.01
        
        # # congestion_lock.acquire()   
        # for idx in range(LAST_ACK + 1, curr):
        #     try:
        #         if ((timer - TIME_STAMP_ARR[idx][0]) > heur):
        #             sock.send(congestion_buffer[idx])
                    
        #             congestion_lock.acquire()  
        #             LAST_ACK = saved
        #             IN_TRANSIT = 1
        #             congestion_lock.release()
        #             CONGESTION_AVOIDANCE = True
        #             TIME_STAMP_ARR[packetCount][0] = time.time()
        #             break
        #     except:
        #         pass
        #congestion_lock.release()

        # if (found):
        #     found = False
        #     # IN_TRANSIT = 0
        #     CONGESTION_AVOIDANCE = True
        
        # if (IN_TRANSIT > 0 and not TIME_STAMP_ARR[packetCount][1]):
        #     congestion_lock.acquire()
        #     if (time.time() - TIME_STAMP_ARR[packetCount][0] > (max(0.05, AVG_RTT))):
        #         IN_TRANSIT = 0
        #         CONGESTION_AVOIDANCE = True
        #     congestion_lock.release()