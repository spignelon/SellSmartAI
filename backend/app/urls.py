from django.urls import path, include
from .api import (
    PostViewset, ConnectedSocialMediaAPI, UpdateConnectedSocialMediaAPI,
    RecentFetchedPostAPI, UpdateListingAPI, PreviousListingAPI,
    DashboardStatsAPI, ProfileDataAPI, FetchInstagramPostAPI,
    FetchFaceBookPostAPI, ConvertVideoToImagesAPI, Social2AmazonAPI,
    HealthCheckAPI  # Make sure to import this
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewset, basename='posts')

urlpatterns = router.urls
urlpatterns += [
    path('connected_social_media', ConnectedSocialMediaAPI.as_view()),
    path('update_social_media', UpdateConnectedSocialMediaAPI.as_view()),
    path('recent_fetched_post', RecentFetchedPostAPI.as_view()),
    path('update_listing_data', UpdateListingAPI.as_view()),
    path('previous_listing_data', PreviousListingAPI.as_view()),
    path('dashboard_stats', DashboardStatsAPI.as_view()),
    path('profile_data', ProfileDataAPI.as_view()),
    path('social2amazon', Social2AmazonAPI.as_view()),
    path('fetch_latest_instagram_post', FetchInstagramPostAPI.as_view()),
    path('fetch_latest_facebook_post', FetchFaceBookPostAPI.as_view()),
    path('convert_video_to_images', ConvertVideoToImagesAPI.as_view()),
    path('health_check', HealthCheckAPI.as_view(), name='health_check')
]
