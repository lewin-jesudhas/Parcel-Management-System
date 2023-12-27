from tracking_id import generate_tracking_number

import qrcode
import numpy as np

tracking_number = 0

def get_tracking_number():
    return tracking_number

def create_tracking_number():
    global tracking_number
    tracking_number = generate_tracking_number(10)
    print(tracking_number)
    data = str(tracking_number)
    # instantiate QRCode object
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    print(qr)
    # add data to the QR code
    qr.add_data(data)
    # compile the data into a QR code array
    qr.make()
    # print the image shape
    print("The shape of the QR image:", np.array(qr.get_matrix()).shape)
    # transfer the array into an actual image
    img = qr.make_image(fill_color="black", back_color="white")
    # save it to a file
    filename=data+".png"
    img.save(filename)

    # def generate_qr_code(data, filename):
    #     # instantiate QRCode object
    #     qr = qrcode.QRCode(version=1, box_size=10, border=4)

    #     # add data to the QR code
    #     qr.add_data(data)

    #     # compile the data into a QR code array
    #     qr.make()

    #     # print the image shape
    #     qr_matrix = np.array(qr.get_matrix())
    #     print("The shape of the QR image:", qr_matrix.shape)

    #     # transfer the array into an actual image
    #     img = qr.make_image(fill_color="white", back_color="black")

    #     # save it to a file
    #     img.save(filename)