import cv2
from pyzbar.pyzbar import decode
import csv
from datetime import datetime
import numpy as np

def initialize_camera():
    """Initialize the webcam"""
    return cv2.VideoCapture(0)

def parse_qr_data(data):
    """Parse tab-delimited QR code data into a list"""
    return [item.strip() for item in data.split('\t')]

def get_headers(parsed_data):
    """Generate CSV headers based on number of fields"""
    # Put real headers in once app is updated.
    return [f'Field_{i+1}' for i in range(len(parsed_data))]

def scan_qr_codes():
    """Main function to scan QR codes and save to CSV"""
    camera = initialize_camera()
    if not camera.isOpened():
        raise Exception("Could not open camera")

    # Set to store unique QR codes
    scanned_codes = set()
    parsed_codes = []  # List to maintain order for CSV
    headers = None
    
    # Prepare CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"qr_codes_{timestamp}.csv"
    
    print("QR Code Scanner Started")
    print("Press 'q' to quit when finished")
    print("Successfully scanned codes:", len(scanned_codes))

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Decode QR codes in current frame
            decoded_objects = decode(frame)
            
            # Process any QR codes found
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                if data not in scanned_codes:
                    scanned_codes.add(data)
                    parsed_data = parse_qr_data(data)
                    
                    # Set headers based on first scanned code
                    if headers is None:
                        headers = get_headers(parsed_data)
                    
                    parsed_codes.append(parsed_data)
                    print(f"\nNew code scanned! Count: {len(scanned_codes)}")
                    print(f"Latest code: {data}")
                    
                    # Draw rectangle around QR code
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(
                            np.array([point for point in points], dtype=np.float32))
                        points = hull
                    
                    # Draw the rectangle
                    cv2.polylines(frame, [np.array(points, np.int32)],
                                True, (0, 255, 0), 3)

            # Show the frame
            cv2.imshow('QR Code Scanner', frame)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Clean up
        camera.release()
        cv2.destroyAllWindows()
        
        # Save to CSV
        if parsed_codes:
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)  # Write headers
                for code_data in parsed_codes:
                    writer.writerow(code_data)
            print(f"\nSaved {len(scanned_codes)} unique codes to {csv_filename}")
        else:
            print("\nNo codes were scanned")

if __name__ == "__main__":
    try:
        scan_qr_codes()
    except Exception as e:
        print(f"An error occurred: {str(e)}")