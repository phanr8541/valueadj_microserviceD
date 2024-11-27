import zmq
import csv
import os
import time


class WishlistService:
    def __init__(self, file_name="wishlist.csv"):
        self.file_name = file_name
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        self.initialize_wishlist()

    def initialize_wishlist(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Set', 'Year', 'Value'])  # Header for wishlist

    def add_card_to_wishlist(self, card_data):
        print("Processing request to add card to wishlist...")
        time.sleep(2)  # Add a 2-second delay to simulate processing times

        with open(self.file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(card_data)

        print(f"Added card to wishlist: {card_data}")

    def get_current_wishlist(self):
        """Retrieve the current wishlist from the file and return a formatted string."""
        if not os.path.exists(self.file_name):
            return "You don't have anything in your wishlist yet!"

        with open(self.file_name, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            wishlist = [row for row in reader]

        if not wishlist:
            return "You don't have anything in your wishlist yet!"

        response = "Here is your current wishlist:\n"
        for idx, card in enumerate(wishlist, 1):
            response += (f"{idx}. Card Name: {card[0]}, "
                         f"Set Name: {card[1]}, "
                         f"Year: {card[2]}, "
                         f"Value: ${card[3]}\n")
        return response

    def edit_card_in_wishlist(self, old_name, updated_card_data):
        """Edit a card in the wishlist by name."""
        try:
            updated = False
            with open(self.file_name, 'r', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)

            with open(self.file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                for row in rows:
                    if row and row[0] == old_name:  # Match card by name
                        writer.writerow(updated_card_data)
                        updated = True
                    else:
                        writer.writerow(row)

            if updated:
                return "Card updated successfully!"
            else:
                return "Card not found in wishlist."
        except Exception as e:
            return f"Error while editing wishlist: {e}"

    def listen(self):
        print("Wishlist service is listening for requests...")
        while True:
            try:
                # Receive JSON request from the client
                message = self.socket.recv_json()
                command = message.get('command')

                # Log received command
                print(f"Received command: {command}")
                print("Processing request...")  # Log to show processing starts
                time.sleep(1)  # Simulate processing delay

                if command == 'display':
                    response = self.get_current_wishlist()
                    self.socket.send_string(response)

                elif command == 'add':
                    card_data = [
                        message.get('name'),
                        message.get('set_name'),
                        message.get('year'),
                        message.get('value')
                    ]
                    if all(card_data):
                        self.add_card_to_wishlist(card_data)
                        self.socket.send_string("Card added to wishlist successfully!")
                    else:
                        self.socket.send_string("Error: Missing card data fields.")

                elif command == 'edit':
                    old_name = message.get('old_name')
                    updated_card_data = [
                        message.get('name'),
                        message.get('set_name'),
                        message.get('year'),
                        message.get('value')
                    ]
                    response = self.edit_card_in_wishlist(old_name, updated_card_data)
                    self.socket.send_string(response)

                else:
                    self.socket.send_string("Invalid command")

                print("Request processed successfully.")  # Log processing complete
            except Exception as e:
                print(f"Error: {e}")
                self.socket.send_string(f"Error: {e}")


if __name__ == "__main__":
    service = WishlistService()
    service.listen()
