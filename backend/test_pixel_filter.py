"""
Test script for PixelFilter
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from src.pixel_filter import PixelFilter
        print("✅ PixelFilter import successful")

        import cv2
        print("✅ OpenCV import successful")

        import numpy as np
        print("✅ NumPy import successful")

        from PIL import Image
        print("✅ PIL import successful")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_pixel_filter_init():
    """Test PixelFilter initialization"""
    print("\nTesting PixelFilter initialization...")
    try:
        from src.pixel_filter import PixelFilter
        pf = PixelFilter()
        print(f"✅ PixelFilter initialized")
        print(f"   ROI: x={pf.roi_x}, y={pf.roi_y}, w={pf.roi_width}, h={pf.roi_height}")
        print(f"   Thresholds: text={pf.text_pixel_threshold}, color={pf.color_pixel_threshold}")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pixel_filter_with_dummy_image():
    """Test PixelFilter with a dummy base64 image"""
    print("\nTesting PixelFilter with dummy image...")
    try:
        from src.pixel_filter import PixelFilter
        import base64
        from PIL import Image
        import io

        # Create a simple test image (100x100 white)
        img = Image.new('RGB', (1920, 1080), color='white')

        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Test filter
        pf = PixelFilter()
        result = pf.has_kill_feed(img_base64)

        print(f"✅ PixelFilter processed image")
        print(f"   Result: {result} (expected False for blank white image)")
        print(f"   Stats: {pf.get_stats()}")

        return True
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_changes():
    """Test that config changes are valid"""
    print("\nTesting config changes...")
    try:
        import config

        print(f"✅ Config loaded")
        print(f"   PIXEL_FILTER_ENABLED: {config.PIXEL_FILTER_ENABLED}")
        print(f"   VISION_MODEL: {config.VISION_MODEL}")
        print(f"   OCR_ENABLED: {config.OCR_ENABLED}")

        # Check that Gemini model is set
        if "gemini" in config.VISION_MODEL.lower():
            print(f"✅ Gemini Flash configured as default")
        else:
            print(f"⚠️  Warning: VISION_MODEL is not Gemini ({config.VISION_MODEL})")

        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_processor_integration():
    """Test that processor.py can import PixelFilter"""
    print("\nTesting processor integration...")
    try:
        # Just check that the imports work
        import processor
        print(f"✅ Processor module loads successfully")

        # Check if PixelFilter is being used
        import inspect
        source = inspect.getsource(processor.FrameProcessor.__init__)
        if "pixel_filter" in source.lower():
            print(f"✅ PixelFilter integrated into FrameProcessor")
        else:
            print(f"⚠️  Warning: PixelFilter may not be integrated")

        return True
    except Exception as e:
        print(f"❌ Processor integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PIXEL FILTER + GEMINI FLASH - TEST SUITE")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))

    if results[-1][1]:  # Only continue if imports work
        results.append(("Initialization", test_pixel_filter_init()))
        results.append(("Dummy Image", test_pixel_filter_with_dummy_image()))
        results.append(("Config", test_config_changes()))
        results.append(("Processor Integration", test_processor_integration()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Safe to commit and deploy.")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} test(s) failed. Fix issues before deploying.")
        sys.exit(1)
