from twilio.rest import Client
# import cv2
import random
from abc import ABC, abstractmethod
from AbstractQRHandler import AbstractQRHandler

account_sid = 'AC29747632c3c6384a632850475540b693'
auth_token = '3e1baf5117e3e2f8085fd8a9bcbd2274'
detector = cv2.QRCodeDetector()
client = Client(account_sid, auth_token)

class Observer(ABC):
    @abstractmethod
    def update(self, otp, tracking_id):
        pass

class OTPNotifier:
    def __init__(self):
        self.observers = set()

    def register_observer(self, observer):
        self.observers.add(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, otp, tracking_id):
        for observer in self.observers:
            observer.update(otp, tracking_id)

class OTPWhatsAppObserver(Observer):
    def update(self, otp, tracking_id):
        self.send_otp_via_whatsapp('whatsapp:+919449225710', otp)

    def send_otp_via_whatsapp(self, to, otp):
        # Sending the OTP using twilio on WhatsApp
        from_whatsapp_number = 'whatsapp:+14155238886'
        message_body = f'Your OTP is: {otp}'
        message = client.messages.create(
            from_=from_whatsapp_number,
            body=message_body,
            to=to
        )
        print(message.sid)

class QRHandler(AbstractQRHandler, OTPNotifier):
    def __init__(self, tracking_data):
        super().__init__()
        self.tracking_data = tracking_data

    def scan_qr(self):
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            data, bbox, _ = detector.detectAndDecode(frame)

            if data:
                for tracking_info in self.tracking_data:
                    if data.strip() in tracking_info:
                        otp = self.generate_otp()
                        print('Generated OTP:', otp)
                        self.notify_observers(otp, data.strip())
                        return {"otp": otp, "tracking_id": data.strip()}

            if bbox is not None and len(bbox) >= 2:
                for i in range(len(bbox)):
                    cv2.line(frame, tuple(map(int, bbox[i][0])), tuple(map(int, bbox[(i + 1) % len(bbox)][0])), color=(255, 0, 0), thickness=2)

            cv2.imshow("QR Code Scanner", frame)

            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def generate_otp(self):
        return random.randint(1000, 9999)
