class Node:
   def __init__(self, idx, data=None):
      self.data = data
      self.next = None
      self.back = None
      self.sent = False
      self.index = idx

   def set_sent(self):
      self.sent = True
   
   def get_data(self):
      return self.data

   def get_next(self):
      return self.next
   
   def was_sent(self):
      return self.sent

   def get_idx(self):
      return self.index
   
class dLinkedList:
   def __init__(self):
      self.head = Node(-1)
      self.length = 0
      self.last = self.head
      self.tail = Node(-1)

   def get_start(self):
      return self.head.next

   def insert(self, value, idx):
      node = Node(data=value, idx=idx)
      
      node.back = self.last
      node.next = self.tail
      self.last.next = node
      self.last = node
      self.length += 1
      return node

   def remove(self, pointer):
      left = pointer.back
      right = pointer.next

      left.next = right
      right.back = left
      self.length -= 1

   def print_ll(self):
      printval = self.head
      while (printval):
         print(printval.data)
         printval = printval.next

# ll = dLinkedList()
# arr = [None]*10

# for i in range(1,10):
#   n = ll.insert(i)
#   arr[i] = n

# ll.remove(arr[5])
# ll.remove(arr[8])
# node = ll.get_start()
# for i in range(0, ll.length):
#    print(node.data)
#    node = node.next