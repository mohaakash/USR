import cv2
import numpy as np

def create_chessboard_image(chessboard_size, square_size, output_file):
    # chessboard_size: (number of internal corners along width, height)
    # square_size: size of one square in pixels
    width_corners, height_corners = chessboard_size
    img_width = (width_corners + 1) * square_size
    img_height = (height_corners + 1) * square_size

    # Create a white canvas
    chessboard = np.ones((img_height, img_width), dtype=np.uint8) * 255  # Start with a white image

    # Loop to draw the squares
    for row in range(height_corners + 1):
        for col in range(width_corners + 1):
            # Check if the square should be black or white
            if (row + col) % 2 == 0:
                x_start = col * square_size
                y_start = row * square_size
                chessboard[y_start:y_start + square_size, x_start:x_start + square_size] = 0  # Black square

    # Convert to a BGR image (3 channels) so we can save it as a color image
    chessboard_bgr = cv2.cvtColor(chessboard, cv2.COLOR_GRAY2BGR)

    # Save the generated chessboard image
    cv2.imwrite(output_file, chessboard_bgr)
    print(f"Chessboard image saved as {output_file}")

    # Optionally, show the generated chessboard
    cv2.imshow("Chessboard", chessboard_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    chessboard_size = (8, 4)  # (internal corners along width, height)
    square_size = 100  # Size of each square in pixels
    output_file = "chessboard_8x4.png"

    create_chessboard_image(chessboard_size, square_size, output_file)
