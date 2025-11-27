# backend/utils/geocode_arcgis.py

from geopy.geocoders import ArcGIS

class ArcGISGeocoder:
    def __init__(self):
        self.geolocator = ArcGIS(timeout=10)

    def geocode(self, address: str):
        try:
            loc = self.geolocator.geocode(address)
            if loc:
                return float(loc.latitude), float(loc.longitude)
        except:
            pass
        return None, None
