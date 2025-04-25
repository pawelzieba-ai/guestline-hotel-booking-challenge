import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta

def load_data(hotels_path, bookings_path):
    try:
        with open(hotels_path) as hfile:
            hotels = json.load(hfile)
    except FileNotFoundError:
        print(f"Error: Hotels file '{hotels_path}' not found.")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in hotels file - {e}")
        return None, None

    try:
        with open(bookings_path) as bfile:
            bookings = json.load(bfile)
    except FileNotFoundError:
        print(f"Error: Bookings file '{bookings_path}' not found.")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in bookings file - {e}")
        return None, None

    return hotels, bookings

def check_availability(hotels, bookings, hotel_id, start_date, end_date, room_type):
    rooms = [room['roomId'] for h in hotels if h['id'] == hotel_id for room in h['rooms'] if room['roomType'] == room_type]
    room_count = len(rooms)

    booked = defaultdict(int)
    for booking in bookings:
        if booking['hotelId'] == hotel_id and booking['roomType'] == room_type:
            if not (booking['departure'] <= start_date or booking['arrival'] > end_date):
                for day in range(int(booking['arrival']), int(booking['departure'])):
                    booked[str(day)] += 1

    max_booked = max(booked.values(), default=0)
    return room_count - max_booked

def search_availability(hotels, bookings, hotel_id, days, room_type):
    today = datetime.today()
    ranges = []
    current_start = None
    current_end = None
    current_count = None

    for i in range(days):
        day = today + timedelta(days=i)
        date_str = day.strftime('%Y%m%d')
        count = check_availability(hotels, bookings, hotel_id, date_str, date_str, room_type)

        if count > 0:
            if current_start is None:
                current_start = date_str
                current_end = date_str
                current_count = count
            elif current_count == count:
                current_end = date_str
            else:
                ranges.append((current_start, current_end, current_count))
                current_start = date_str
                current_end = date_str
                current_count = count
        elif current_start:
            ranges.append((current_start, current_end, current_count))
            current_start = None
            current_end = None
            current_count = None

    if current_start:
        ranges.append((current_start, current_end, current_count))

    return ranges

def run_console(hotels, bookings):
    print("Enter commands (Availability or Search). Press Enter to exit.")
    while True:
        try:
            user_input = input("Enter command: ").strip()
        except EOFError:
            break

        if user_input == "":
            break
        if user_input.startswith("Availability("):
            parts = user_input[12:-1].split(',')
            if len(parts) == 3:
                hotel_id, date, room_type = parts
                availability = check_availability(hotels, bookings, hotel_id.strip(), date.strip(), date.strip(), room_type.strip())
                print(availability)
            elif len(parts) == 4:
                hotel_id, start_date, end_date, room_type = parts
                availability = check_availability(hotels, bookings, hotel_id.strip(), start_date.strip(), end_date.strip(), room_type.strip())
                print(availability)
            else:
                print("Invalid Availability format.")
        elif user_input.startswith("Search("):
            try:
                hotel_id, days, room_type = user_input[7:-1].split(',')
                results = search_availability(hotels, bookings, hotel_id.strip(), int(days.strip()), room_type.strip())
                print(", ".join(f"({r[0]}-{r[1]}, {r[2]})" for r in results))
            except ValueError:
                print("Invalid Search format.")
        else:
            print("Invalid command")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hotels', required=False, default='hotels.json')
    parser.add_argument('--bookings', required=False, default='bookings.json')
    args = parser.parse_args()

    hotels, bookings = load_data(args.hotels, args.bookings)
    if hotels is None or bookings is None:
        print("Exiting due to previous errors.")
        return

    run_console(hotels, bookings)

if __name__ == '__main__':
    main()
