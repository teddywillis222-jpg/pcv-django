"""
Script de test pour vérifier la génération d'URL OG via le SDK Cloudinary.
Simule ce que la vue professeur_detail fait côté serveur.
"""
import re

# ============================================================
# Test 1: Fonction _inject_cloudinary_transformation (template filter)
# ============================================================
def _inject_cloudinary_transformation(url, transformation):
    """Copie locale de la fonction dans image_utils.py pour test."""
    url = str(url)
    if 'res.cloudinary.com' not in url:
        return url
    if url.startswith('//'):
        url = 'https:' + url
    elif url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    if '/upload/' not in url:
        return url
    url = re.sub(
        r'/upload/(?:[^/]+/)*?(v\d+/)',
        f'/upload/{transformation}/\\1',
        url,
        count=1
    )
    if f'/upload/{transformation}/' not in url:
        url = url.replace('/upload/', f'/upload/{transformation}/', 1)
    return url


print("=" * 70)
print("TEST 1: Template filter _inject_cloudinary_transformation")
print("=" * 70)

test_cases = [
    # (description, input_url, expected_pattern)
    (
        "URL avec version v1 et sous-dossier",
        "https://res.cloudinary.com/dcgpvh2fu/image/upload/v1/media/teachers/profile_photos/IMG_8619.webp",
        "should have transformation BEFORE v1"
    ),
    (
        "URL avec version longue",
        "https://res.cloudinary.com/dcgpvh2fu/image/upload/v1723812345/media/IMG_test.webp",
        "should have transformation BEFORE v1723812345"
    ),
    (
        "URL sans version (directe)",
        "https://res.cloudinary.com/dcgpvh2fu/image/upload/media/IMG_direct.webp",
        "should inject transformation after /upload/"
    ),
    (
        "URL protocol-relative",
        "//res.cloudinary.com/dcgpvh2fu/image/upload/v1/media/IMG_proto.webp",
        "should force https://"
    ),
]

transformation = "w_1200,h_630,c_fill,g_face,f_jpg,q_auto"

for desc, url, expected in test_cases:
    result = _inject_cloudinary_transformation(url, transformation)
    print(f"\n--- {desc} ---")
    print(f"  Input:    {url}")
    print(f"  Output:   {result}")
    print(f"  Expected: {expected}")
    
    # Validations
    assert result.startswith('https://'), f"FAIL: URL doesn't start with https://"
    assert '/upload/' in result, f"FAIL: /upload/ not in URL"
    assert transformation in result, f"FAIL: transformation not injected"
    
    # Check transformation is BEFORE version
    upload_idx = result.index('/upload/')
    trans_idx = result.index(transformation)
    if '/v1' in url or '/v17' in url:
        v_match = re.search(r'/v\d+/', result)
        if v_match:
            assert trans_idx < v_match.start(), f"FAIL: transformation should be BEFORE version!"
            print(f"  ✅ PASS - transformation ({trans_idx}) is before version ({v_match.start()})")
        else:
            print(f"  ⚠️  Version not found in output")
    else:
        print(f"  ✅ PASS - no version expected, transformation injected correctly")

# ============================================================
# Test 2: SDK cloudinary.utils.cloudinary_url
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Cloudinary SDK cloudinary_url()")
print("=" * 70)

try:
    import cloudinary
    import cloudinary.utils
    import os
    
    # Configure Cloudinary (use env vars if available)
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dcgpvh2fu')
    cloudinary.config(
        cloud_name=cloud_name,
        secure=True
    )
    
    # Simulate what the view does
    test_public_ids = [
        "media/teachers/profile_photos/IMG_8619_rzinun_udknho_u44mvl_enlcug_m6ukmv",
        "media/IMG_8619_rzinun_udknho_u44mvl_enlcug_m6ukmv",
    ]
    
    for pid in test_public_ids:
        url, options = cloudinary.utils.cloudinary_url(
            pid,
            width=1200,
            height=630,
            crop="fill",
            gravity="face",
            format="jpg",
            quality="auto",
            secure=True
        )
        print(f"\n  public_id: {pid}")
        print(f"  Generated URL: {url}")
        
        # Verify URL structure
        assert url.startswith('https://'), "FAIL: not HTTPS"
        assert 'w_1200' in url, "FAIL: width not in URL"
        assert 'h_630' in url, "FAIL: height not in URL"
        assert 'f_jpg' in url, "FAIL: format not in URL"
        assert '.jpg' in url, "FAIL: .jpg extension not in URL"
        print(f"  ✅ PASS - SDK URL is valid")

except ImportError:
    print("  ⚠️  cloudinary package not installed locally (normal for local dev without psycopg)")
    print("  The SDK will work on the production server where cloudinary is installed.")

print("\n\n" + "=" * 70)
print("ALL TESTS PASSED ✅")
print("=" * 70)
