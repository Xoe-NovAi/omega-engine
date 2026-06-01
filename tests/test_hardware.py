class TestHardware:
    def test_imports(self):
        from omega.hardware import detect_hardware, HardwareProfile
        assert detect_hardware is not None
        assert HardwareProfile is not None

    def test_detect_hardware_returns_profile(self):
        from omega.hardware import detect_hardware
        profile = detect_hardware()
        assert hasattr(profile, "total_ram_gb")
        assert hasattr(profile, "available_ram_gb")
        assert hasattr(profile, "cpu_count")
        assert hasattr(profile, "is_zen2")
        assert isinstance(profile.total_ram_gb, (int, float))
        assert isinstance(profile.cpu_count, int)
