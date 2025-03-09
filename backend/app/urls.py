from rest_framework import routers
from .api import PostViewset
from django.urls import path
from .api import ConnectedSocialMediaAPI, UpdateConnectedSocialMediaAPI, RecentFetchedPostAPI, UpdateListingAPI, PreviousListingAPI, DashboardStatsAPI, ProfileDataAPI, Social2AmazonAPI
from .api import FetchInstagramPostAPI
from .api import FetchFaceBookPostAPI
from .api import ConvertVideoToImagesAPI

router = routers.SimpleRouter()
router.register(r'posts', PostViewset, basename="posts")

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
    path('convert_video_to_images', ConvertVideoToImagesAPI.as_view())
]
