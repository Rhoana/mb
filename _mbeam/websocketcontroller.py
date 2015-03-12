import json

class WebSocketController(object):

  def __init__(self, manager):
    '''
    '''
    self._manager = manager

    self._websocket = None

  def handshake(self, websocket):
    '''
    '''
    self._websocket = websocket

    self.send_data_tree()


  def send_data_tree(self):
    '''
    '''
    if self._websocket:
      output = {}
      output['name'] = 'NEW_DATA'
      output['origin'] = 'SERVER'
      output['value'] = self._manager._data_tree

      self._websocket.send(json.dumps(output))


  def on_message(self, message):
    '''
    '''
    message = json.loads(message)
    
    if (message['name'] == 'CONTENT'):

      content = self._manager.get_content(message['value'])

      output = {}
      output['name'] = 'CONTENT'
      output['origin'] = message['origin']
      output['value'] = content

      self._websocket.send(json.dumps(output))
