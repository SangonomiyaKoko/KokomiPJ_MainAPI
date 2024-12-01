class ServiceStatus:
    _is_available = True  # 类属性，所有实例共享

    @classmethod
    def service_set_available(cls):
        """设置服务为可用"""
        cls._is_available = True

    @classmethod
    def service_set_unavailable(cls):
        """设置服务为不可用"""
        cls._is_available = False

    @classmethod
    def is_service_available(cls):
        """检查服务是否可用"""
        return cls._is_available
