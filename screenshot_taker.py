import Quartz, time
import LaunchServices
from Cocoa import NSURL
import Quartz.CoreGraphics as CG
global counter
counter = 0
FILE_NAME = "screenshot_name.jpg"

def screenshot(path, region = None):
    """region should be a CGRect, something like:

    >>> import Quartz.CoreGraphics as CG
    >>> region = CG.CGRectMake(0, 0, 100, 100)
    >>> sp = ScreenPixel()
    >>> sp.capture(region=region)

    The default region is CG.CGRectInfinite (captures the full screen)
    """

    if region is None:
        region = CG.CGRectInfinite

    # Create screenshot as CGImage
    image = CG.CGWindowListCreateImage(
        region,
        CG.kCGWindowListOptionOnScreenOnly,
        CG.kCGNullWindowID,
        CG.kCGWindowImageDefault)

    dpi = 72 # FIXME: Should query this from somewhere, e.g for retina displays

    url = NSURL.fileURLWithPath_(path)

    dest = Quartz.CGImageDestinationCreateWithURL(
        url,
        LaunchServices.kUTTypePNG, # file type
        1, # 1 image in file
        None
        )

    properties = {
        Quartz.kCGImagePropertyDPIWidth: dpi,
        Quartz.kCGImagePropertyDPIHeight: dpi,
        }

    # Add the image to the destination, characterizing the image with
    # the properties dictionary.
    Quartz.CGImageDestinationAddImage(dest, image, properties)

    # When all the images (only 1 in this example) are added to the destination, 
    # finalize the CGImageDestination object. 
    Quartz.CGImageDestinationFinalize(dest)

def make_screenshot():
    global counter
    region = CG.CGRectMake(28, 46, 640, 640)
    screenshot_time = time.time()
    screenshot(FILE_NAME, region=region)
    # save_screenshot(counter)
    counter+=1
    return FILE_NAME, screenshot_time
    
def save_screenshot(number):
    region = CG.CGRectMake(28, 46, 640, 640)
    screenshot("testscreenshot_partial"+str(number)+".png", region=region)
    # time.sleep(0.2)



if __name__ == '__main__':
    # Capture full screen
    # screenshot("testscreenshot_full.png")

    # Capture region (100x100 box from top-left)
    time.sleep(2)
    region = CG.CGRectMake(28, 46, 640, 640)
    for i in xrange(50):
        screenshot("testscreenshot_partial"+str(i)+".png", region=region)
        time.sleep(0.2)
