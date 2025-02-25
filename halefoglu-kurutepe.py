# --------------------------------------
# SECTION 1: IMPORTING REQUIRED LIBRARIES
# --------------------------------------
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import numpy as np
import tkinter as tk
from tkinter import messagebox
from shapely.geometry import Polygon
from shapely.affinity import rotate, translate


# --------------------------------------
# SECTION 2: POINT SELECTION FUNCTION
# --------------------------------------
def select_points_on_plot():
    """
    Allows the user to select points on a plot.
    """
    print("Click on points in the plot. Right-click or press 'Enter' to finish.")
    fig, ax = plt.subplots(figsize=(5, 5))
    plt.title("Point Selection")
    plt.xlabel("X (0-50)")
    plt.ylabel("Y (0-50)")
    plt.grid(True)
    plt.xlim(0, 50)
    plt.ylim(0, 50)

    # User selects points
    points = plt.ginput(n=-1, timeout=0)
    plt.close()
    return np.array(points)


# --------------------------------------
# SECTION 3: SHAPE OPERATIONS
# --------------------------------------
def create_shapely_polygon(points):
    """
    Create a Shapely polygon from given points.
    """
    return Polygon(points)


def create_rotated_shapes(shape, angles):
    """
    Create rotated versions of the given shape for each angle in the list.
    """
    rotated_shapes = {}
    for angle in angles:
        rotated_shapes[angle] = rotate(shape, angle, origin='centroid', use_radians=False)
    return rotated_shapes


def can_place(candidate, placed_shapes, bounds):
    """
    Check if the candidate shape can be placed without overlapping or going out of bounds.
    """
    if not bounds.contains(candidate):
        return False
    for existing_shape in placed_shapes:
        if candidate.intersects(existing_shape):
            return False
    return True


def place_shapes(container, shape, angles, grid_step=10):
    """
    Place as many rotated instances of a shape as possible within the container.
    """
    bounds = container.bounds
    rotated_shapes = create_rotated_shapes(shape, angles)
    placed_shapes = []

    x_min, y_min, x_max, y_max = bounds
    for x in np.arange(x_min, x_max, grid_step):
        for y in np.arange(y_min, y_max, grid_step):
            for angle, rotated in rotated_shapes.items():
                candidate = translate(rotated, xoff=x, yoff=y)
                if can_place(candidate, placed_shapes, container):
                    placed_shapes.append(candidate)
                    break
    return placed_shapes


# --------------------------------------
# SECTION 4: DISPLAYING THE CUTTING AREA
# --------------------------------------
def draw_full_convex_hull(points, x_limit, y_limit):
    """
    Fills the cutting area with rotated Convex Hull shapes using the selected points.
    """
    if len(points) < 3:
        messagebox.showerror("Error", "At least 3 points must be selected!")
        return

    # Calculate the Convex Hull
    convex_hull = ConvexHull(points)
    hull_points = points[convex_hull.vertices]

    # Create the original shape
    original_shape = create_shapely_polygon(hull_points)

    # Define the container area
    container = Polygon([(0, 0), (x_limit, 0), (x_limit, y_limit), (0, y_limit)])

    # Place shapes within the container
    angles = [0, 90, 180, 270]  # Allowed rotation angles
    placed_shapes = place_shapes(container, original_shape, angles, grid_step=10)

    # Visualization
    plt.figure(figsize=(12, 6))
    plt.xlim(0, x_limit)
    plt.ylim(0, y_limit)
    plt.grid(True)
    plt.title("Cutting Area Layout")
    plt.xlabel("X")
    plt.ylabel("Y")

    # Draw the container
    plt.plot(*container.exterior.xy, color="black")

    # Draw placed shapes
    for shape in placed_shapes:
        x, y = shape.exterior.xy
        plt.fill(x, y, color="blue", alpha=0.6)

    # Efficiency calculation
    total_shape_area = sum(shape.area for shape in placed_shapes)
    total_cutting_area = container.area
    utilization_percentage = (total_shape_area / total_cutting_area) * 100
    plt.text(x_limit / 2, -20, 
             f"Cutting Area Efficiency: {utilization_percentage:.2f}%", 
             fontsize=12, ha="center", color="red")
    plt.show()


# --------------------------------------
# SECTION 5: GUI OPERATIONS
# --------------------------------------
def start_gui():
    """
    Starts the Tkinter GUI and binds operations.
    """
    def on_select_points():
        global points
        points = select_points_on_plot()
        if len(points) < 3:
            points = None
            messagebox.showwarning("Warning", "At least 3 points must be selected!")
        else:
            messagebox.showinfo("Success", "Points have been successfully selected!")

    def on_display_cutting_area():
        if points is None or len(points) < 3:
            messagebox.showerror("Error", "Please select points first!")
            return
        draw_full_convex_hull(points, x_limit=1000, y_limit=200)

    root = tk.Tk()
    root.title("Laser Cutting Layout Optimization")
    root.geometry("400x200")

    # Buttons
    select_points_button = tk.Button(root, text="Select Points", command=on_select_points, height=2, width=20)
    select_points_button.pack(pady=10)

    display_cutting_button = tk.Button(root, text="Show Cutting Area", command=on_display_cutting_area, height=2, width=20)
    display_cutting_button.pack(pady=10)

    root.mainloop()


# --------------------------------------
# SECTION 6: STARTING THE PROGRAM
# --------------------------------------
if __name__ == "__main__":
    points = None  # Global variable
    start_gui()
