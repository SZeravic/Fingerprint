# Python openCV Fingerprint Recognition

Fingerprint recognition with SKimage and OpenCV

Requirements:
- NumPy     (numpy)
- SKimage   (scikit-image)
- OpenCV2   (opencv-python)

Works by extracting minutiae points using harris corner detection.

Uses SIFT (ORB) go get formal descriptors around the keypoints with brute-force hamming distance and then analyzes the returned matches using thresholds.
