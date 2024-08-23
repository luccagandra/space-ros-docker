import rclpy
from rclpy.node import Node
from std_msgs.msg import String



class MyPublisher(Node):
    def __init__(self):
        super().__init__('my_publisher')
        self.publisher_ = self.create_publisher(String, 'my_topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello, ROS 2!'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = MyPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

import tkinter as tk
from tkinter import messagebox

def submit():
    latitude = latitude_entry.get()
    longitude = longitude_entry.get()
    
    # Validate inputs
    try:
        lat = float(latitude)
        lon = float(longitude)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            messagebox.showinfo("Success", f"Latitude: {lat}\nLongitude: {lon}")
        else:
            messagebox.showerror("Error", "Latitude must be between -90 and 90.\nLongitude must be between -180 and 180.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for latitude and longitude.")

# Create the main window
root = tk.Tk()
root.title("Latitude and Longitude Input")

# Create and place the latitude label and entry field
latitude_label = tk.Label(root, text="Latitude:")
latitude_label.grid(row=0, column=0, padx=10, pady=10)
latitude_entry = tk.Entry(root)
latitude_entry.grid(row=0, column=1, padx=10, pady=10)

# Create and place the longitude label and entry field
longitude_label = tk.Label(root, text="Longitude:")
longitude_label.grid(row=1, column=0, padx=10, pady=10)
longitude_entry = tk.Entry(root)
longitude_entry.grid(row=1, column=1, padx=10, pady=10)

# Create and place the submit button
submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.grid(row=2, column=0, columnspan=2, pady=20)

# Run the main loop
root.mainloop()


if __name__ == '__main__':
    main()
