
class MyQueue():
  def __init__(self,limit=100):
    self.limit = limit
    self.queue = []
    pass
  def insertItem(self,item):
    if item is None:
      return
    else:
      if(len(self.queue)>=self.limit):
        firstitem = self.queue[0]
        self.queue.remove(firstitem)
        self.queue.append(item)
      else:
        self.queue.append(item)
  def getAllItems(self):
    return self.queue
