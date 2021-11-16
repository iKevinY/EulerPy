
# code for linked_list

# node
class node:
    def __init__(self, node_data):
        self.data = node_data
        self.next = None

# forward linked list
class fll:
    def __init__(self):
        self.head = None
    def push(self, node_data):
       node1 = node(node_data)
       node1.next= self.head
       self.head = node1


"""
# test code

solved = fll();
solved.push(25)
solved.push(50)

a = solved.head
while(a):
    print(a.data)
    a = a.next

"""
