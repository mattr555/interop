"""Tests for the obstacles module."""

import json
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.models.stationary_obstacle import StationaryObstacle
from auvsi_suas.models.waypoint import Waypoint
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

obstacle_url = reverse('auvsi_suas:obstacles')


class TestObstaclesViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(obstacle_url)
        self.assertEqual(403, response.status_code)


class TestObstaclesView(TestCase):
    """Tests the obstacles view."""

    def create_stationary_obstacle(self, lat, lon, radius, height):
        """Create a new StationaryObstacle model.

        Args:
            lat: Latitude of centroid
            lon: Longitude of centroid
            radius: Cylinder radius
            height: Cylinder height

        Returns:
            Saved StationaryObstacle
        """
        gps = GpsPosition(latitude=lat, longitude=lon)
        gps.save()

        obstacle = StationaryObstacle(
            gps_position=gps, cylinder_radius=radius, cylinder_height=height)
        obstacle.save()
        return obstacle

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'email@example.com',
                                             'testpass')
        self.user.save()
        self.client.force_login(self.user)

        # Create an active mission.
        pos = GpsPosition()
        pos.latitude = 10
        pos.longitude = 10
        pos.save()
        config = MissionConfig()
        config.is_active = True
        config.home_pos = pos
        config.emergent_last_known_pos = pos
        config.off_axis_odlc_pos = pos
        config.air_drop_pos = pos
        config.save()

        # Add a couple of stationary obstacles
        obst = self.create_stationary_obstacle(
            lat=38.142233, lon=-76.434082, radius=300, height=500)
        config.stationary_obstacles.add(obst)

        obst = self.create_stationary_obstacle(
            lat=38.442233, lon=-76.834082, radius=100, height=750)
        config.stationary_obstacles.add(obst)

        config.save()

    def test_post(self):
        """POST requests are not allowed."""
        response = self.client.post(obstacle_url)
        self.assertEqual(405, response.status_code)

    def test_correct_json(self):
        """Tests that access is logged and returns valid response."""
        response = self.client.get(obstacle_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertIn('stationaryObstacles', data)
        self.assertEqual(2, len(data['stationaryObstacles']))
        for obstacle in data['stationaryObstacles']:
            self.assertIn('latitude', obstacle)
            self.assertIn('longitude', obstacle)
            self.assertIn('radius', obstacle)
            self.assertIn('height', obstacle)
