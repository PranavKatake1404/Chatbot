import sqlite3
from datetime import datetime

class HotelManagementSystem:
    def __init__(self):
        self.customer_care_number = "1234567890"  # Customer care number
        self.upi_id = "hotel@example.com"  # UPI ID for payment
        self.phone_number = "9876543210"  # Phone number for payment
        self.connect_to_database()

    def connect_to_database(self):
        self.connection = sqlite3.connect('hotel_management.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS room_bookings
                             (id INTEGER PRIMARY KEY,
                             room_number INTEGER NOT NULL,
                             check_in_date TEXT NOT NULL,
                             check_out_date TEXT NOT NULL,
                             guest_name TEXT NOT NULL,
                             ac BOOLEAN NOT NULL,
                             bed_type TEXT NOT NULL,
                             extra_mattress BOOLEAN NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS room_info
                             (id INTEGER PRIMARY KEY,
                             total_rooms INTEGER NOT NULL,
                             total_ac_rooms INTEGER NOT NULL,
                             total_non_ac_rooms INTEGER NOT NULL)''')
        self.connection.commit()
        self.setup_room_info()

    def setup_room_info(self):
        self.cursor.execute("SELECT COUNT(*) FROM room_info")
        count = self.cursor.fetchone()[0]
        if count == 0:
            total_rooms = int(input("Enter total number of rooms: "))
            total_ac_rooms = int(input("Enter total number of AC rooms: "))
            total_non_ac_rooms = total_rooms - total_ac_rooms
            self.cursor.execute("INSERT INTO room_info (total_rooms, total_ac_rooms, total_non_ac_rooms) VALUES (?, ?, ?)",
                                (total_rooms, total_ac_rooms, total_non_ac_rooms))
            self.connection.commit()

    def book_room(self, room_number, check_in_date, check_out_date, guest_name, ac, bed_type, extra_mattress):
        if not self.is_room_available(room_number):
            raise ValueError("Room already booked")
        self.cursor.execute("INSERT INTO room_bookings (room_number, check_in_date, check_out_date, guest_name, ac, bed_type, extra_mattress) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (room_number, check_in_date, check_out_date, guest_name, ac, bed_type, extra_mattress))
        self.connection.commit()
        print(f"Room {room_number} booked successfully for {guest_name} from {check_in_date} to {check_out_date}")

    def cancel_booking(self, room_number):
        self.cursor.execute("DELETE FROM room_bookings WHERE room_number=?", (room_number,))
        self.connection.commit()
        print(f"Booking for room {room_number} canceled successfully")

    def is_room_available(self, room_number):
        self.cursor.execute("SELECT * FROM room_bookings WHERE room_number=?", (room_number,))
        return not self.cursor.fetchone()

    def display_available_rooms(self):
        available_rooms = []
        for room_number in range(101, 151):
            if self.is_room_available(room_number):
                available_rooms.append(room_number)
        if available_rooms:
            print(f"Available rooms: {available_rooms}")
        else:
            print("No rooms available at the moment.")

    def generate_receipt(self, room_number):
        self.cursor.execute("SELECT * FROM room_bookings WHERE room_number=?", (room_number,))
        booking_info = self.cursor.fetchone()
        if not booking_info:
            print("Room not booked")
            return
        
        check_in_date = booking_info[2]
        check_out_date = booking_info[3]
        guest_name = booking_info[4]

        # Assuming room rate is fixed for all types
        room_rate = 4000
        num_days = (datetime.strptime(check_out_date, "%Y-%m-%d") - datetime.strptime(check_in_date, "%Y-%m-%d")).days
        total_room_cost = room_rate * num_days

        # Additional cost for AC rooms
        if booking_info[5]:
            total_room_cost += 500  # Additional charge for AC rooms

        # Additional cost for double bed rooms
        if booking_info[6] == "double":
            total_room_cost += 800  # Additional charge for double bed rooms

        # Additional cost for extra mattress
        if booking_info[7]:
            total_room_cost += 200  # Additional charge for extra mattress

        # Calculate GST (18%)
        gst_rate = 0.18
        gst_amount = total_room_cost * gst_rate

        # Calculate grand total including GST
        grand_total = total_room_cost + gst_amount

        # Print receipt details
        print("\n===== Receipt for Booking =====")
        print(f"Room Number: {room_number}")
        print(f"Customer Name: {guest_name}")
        print(f"GST Number: GST123456789")
        print(f"Check-in Date: {check_in_date}")
        print(f"Check-out Date: {check_out_date}")
        print(f"Total Room Cost: {total_room_cost} INR")
        print(f"GST (18%): {gst_amount} INR")
        print(f"Grand Total: {grand_total} INR")
        print("\n===== Payment Methods =====")
        print("UPI ID: ", self.upi_id)
        print("Phone Number: ", self.phone_number)
        print("\nThank you for choosing our hotel! Visit again soon!\n")

    def display_bookings(self):
        self.cursor.execute("SELECT * FROM room_bookings")
        bookings = self.cursor.fetchall()
        if not bookings:
            print("No bookings found")
            return
        print("Current bookings:")
        for booking in bookings:
            print(f"Room {booking[1]}: {booking[4]} - Check-in: {booking[2]}, Check-out: {booking[3]}")

class HotelManagementChatbot:
    def __init__(self):
        self.hotel_system = HotelManagementSystem()

    def start(self):
        print("Welcome to the Hotel Management Chatbot!")
        while True:
            user_input = input("What would you like to do?\n1.book\n2.cancel\n3.receipt\n4.available\n5.display\n6.enquiry\n7.exit\n")
            if user_input == "1":
                self.book_room()
            elif user_input == "2":
                self.cancel_booking()
            elif user_input == "3":
                self.generate_receipt()
            elif user_input == "4":
                self.display_available_rooms()
            elif user_input == "5":
                self.display_bookings()
            elif user_input == "6":
                self.customer_care_enquiry()
            elif user_input == "7":
                print("Thank you for using the Hotel Management Chatbot!")
                break
            else:
                print("Invalid input. Please try again.")

    def book_room(self):
        try:
            room_number = int(input("Enter room number: "))
            if room_number < 101 or room_number > 150:
                raise ValueError("Invalid room number. Room number must be between 101 and 150.")
            check_in_date = input("Enter check-in date (YYYY-MM-DD): ")
            check_out_date = input("Enter check-out date (YYYY-MM-DD): ")
            guest_name = input("Enter guest name: ")
            ac = self.get_boolean_input("Do you want an AC room? (yes/no): ")
            bed_type = self.get_bed_type()
            extra_mattress = self.get_boolean_input("Do you want an extra mattress? (yes/no): ")
            self.hotel_system.book_room(room_number, check_in_date, check_out_date, guest_name, ac, bed_type, extra_mattress)
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def cancel_booking(self):
        try:
            room_number = int(input("Enter room number to cancel booking: "))
            self.hotel_system.cancel_booking(room_number)
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def generate_receipt(self):
        try:
            room_number = int(input("Enter room number for receipt: "))
            self.hotel_system.generate_receipt(room_number)
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def display_available_rooms(self):
        self.hotel_system.display_available_rooms()

    def display_bookings(self):
        self.hotel_system.display_bookings()

    def customer_care_enquiry(self):
        enquiry = input("Enter your enquiry: ")
        print(f"Customer Care Number: {self.hotel_system.customer_care_number}")
        print("Thank you for contacting customer care. We will get back to you soon.")

    def get_boolean_input(self, prompt):
        while True:
            user_input = input(prompt).lower()
            if user_input == "yes":
                return True
            elif user_input == "no":
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    def get_bed_type(self):
        while True:
            bed_type = input("Enter bed type (single/double): ").lower()
            if bed_type == "single" or bed_type == "double":
                return bed_type
            else:
                print("Invalid input. Please enter 'single' or 'double'.")


# Test the chatbot
chatbot = HotelManagementChatbot()
chatbot.start()
