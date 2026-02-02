class Device:
    def __init__(self, device_id: int):
        """A device is an object that has the ability to send, cancel, and receive alerts"""
        self.device_id = device_id
        self.recipient_list = []
        self.message_list = []
        self.cancelled_messages = []

    def send(self, recipients: list, message: str, timestamp: int, queue: dict) -> None:
        """Send alert to all devices that were previously propagated and schedule reception"""
        for recipient, delay in recipients:
            time = str(int(timestamp) + delay)
            print(f'@{timestamp}: #{self.device_id} SENT ALERT TO #{recipient}: {message}')
            queue[time].append(('RA', recipient, self.device_id, message))

    def cancel(self, recipients: list, message: str, timestamp: int, queue: dict) -> None:
        """Cancel alert to all devices that were previously propagated and schedule cancellation"""
        for recipient, delay in recipients:
            time = str(int(timestamp) + delay)
            print(f'@{timestamp}: #{self.device_id} SENT CANCELLATION TO #{recipient}: {message}')
            queue[time].append(('RC', recipient, self.device_id, message))

    def receive_alert(self, sender: int, message: str, timestamp: int, queue: dict) -> None:
        """Receive alert and forward it along the chain if it wasn't previously sent"""
        print(f'@{timestamp}: #{self.device_id} RECEIVED ALERT FROM #{sender}: {message}')
        if message not in self.message_list:
            self.message_list.append(message)
        if message not in self.cancelled_messages:
            self.send(self.recipient_list, message, timestamp, queue)

    def receive_cancellation(self, sender: int, message: str, timestamp: int, queue: dict) -> None:
        """Cancel alert if it wasn't previously canceled"""
        print(f'@{timestamp}: #{self.device_id} RECEIVED CANCELLATION FROM #{sender}: {message}')

        if message in self.message_list and message not in self.cancelled_messages:
            self.cancelled_messages.append(message)
            self.cancel(self.recipient_list, message, timestamp, queue)