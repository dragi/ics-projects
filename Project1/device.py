class Device:
    def __init__(self, device_id: int):
        self.device_id = device_id
        self.recipient_list = []
        self.message_list = []

    def send(self, recipients: tuple, message: str, timestamp: int, queue: dict, devices: dict):
        for recipient, delay in recipients:
            time = str(int(timestamp) + delay)
            print(f'@{timestamp}: #{self.device_id} SENT ALERT TO #{recipient}: {message}')
            queue[time].append(('RA', recipient, self.device_id, message))
            devices[str(recipient)].message_list.append(message)

    def cancel(self, recipients: tuple, message: str, timestamp: int, queue: dict):
        for recipient, delay in recipients:
            time = str(int(timestamp) + delay)
            print(f'@{timestamp}: #{self.device_id} SENT CANCELLATION TO #{recipient}: {message}')
            queue[time].append(('RC', self.device_id, recipients, message))

    def receive_alert(self, recipient: int, message: str, timestamp: int):
        print(f'@{timestamp}: #{recipient} RECEIVED ALERT FROM #{self.device_id}: {message}')

    def receive_cancellation(self, recipient: int, message: str, timestamp: int, devices: dict):
        print(f'@{timestamp}: #{recipient} RECEIVED CANCELLATION FROM #{self.device_id}: {message}')
        devices[str(recipient)].message_list.remove(message)