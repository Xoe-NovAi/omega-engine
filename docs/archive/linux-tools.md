Technical description
Package: libheif-plugin-libde265
libheif is an ISO/IEC 23008-12:2017 HEIF and AVIF (AV1 Image File Format) file format decoder and encoder. There is partial support for ISO/IEC 23008-12:2022 (2nd Edition) capabilities.
HEIF and AVIF are new image file formats employing HEVC (H.265) or AV1 image coding, respectively, for the best compression ratios currently possible.
libheif supports various codecs provided by plugins for image decoding and encoding.
This package contains the libde265 plugin that uses libde265 to decode HEVC images.
libde265: https://www.libde265.org/

Changes for libheif-plugin-libde265 versions:
Installed version: 1.20.2-1ubuntu0.5
Available version: 1.20.2-1ubuntu0.6

Version 1.20.2-1ubuntu0.6: 

  * SECURITY UPDATE: Integer overflow when parsing uncC.
    - debian/patches/CVE-2026-47709-1.patch: Prevent integer overflow
      when parsing uncC in libheif/codecs/uncompressed/unc_boxes.cc
    - debian/patches/CVE-2026-47709-2.patch: Reject unci images with no ispe
      box in libheif/image-items/unc_image.cc
    - CVE-2026-47709
  * SECURITY UPDATE: Integer overflow in inline mask size calculation
    - debian/patches/CVE-2026-47714.patch: Fix computation of size of inline
      region mask in libheif/region.cc
    - CVE-2026-47714
  * SECURITY UPDATE: OOB read in ImageItem_Grid::decode_grid_tile.
    - debian/patches/CVE-2026-48029.patch: Fix tile coordinates validation
      in rotated images in libheif/api/libheif/heif_tiling.cc and
      libheif/image-items/image_item.cc
    - CVE-2026-48029
  * SECURITY UPDATE: Unbounded heap allocation in sequence parser.
    - debian/patches/CVE-2026-50142.patch: Fix check against security limit
      in libheif/sequences/seq_boxes.cc and ../track.cc
    - CVE-2026-50142


---

Technical description
Package: libcurl4t64
libcurl is an easy-to-use client-side URL transfer library, supporting DICT, FILE, FTP, FTPS, GOPHER, HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, POP3, POP3S, RTMP, RTSP, SCP, SFTP, SMTP, SMTPS, TELNET and TFTP.
libcurl supports SSL certificates, HTTP POST, HTTP PUT, FTP uploading, HTTP form based upload, proxies, cookies, user+password authentication (Basic, Digest, NTLM, Negotiate, Kerberos), file transfer resume, http proxy tunneling and more!
libcurl is free, thread-safe, IPv6 compatible, feature rich, well supported, fast, thoroughly documented and is already used by many known, big and successful companies and numerous applications.
SSL support is provided by OpenSSL.

Changes for libcurl4t64 versions:
Installed version: 8.14.1-2ubuntu1.4
Available version: 8.14.1-2ubuntu1.5

Version 8.14.1-2ubuntu1.5: 

  * SECURITY UPDATE: Use after free in curl_easy_reset.
    - debian/patches/CVE-2026-10536.patch: Deprecate CURLOPT_* in
      include/curl/curl.h, lib/http2.c,
      lib/setopt.c, lib/url.c, and lib/urldata.h
    - CVE-2026-10536
  * SECURITY UPDATE: Improper validation in config2setopts.
    - debian/patches/CVE-2026-12064.patch: Use default protocol properly in
      src/config2setopts.c.
    - CVE-2026-12064
  * debian/patches/CVE-2026-5773.patch: Fix potential edge cases in fix. Thanks to Siddharth Doshi.
  
  ---Technical description
Package: libheif-plugin-aomdec
libheif is an ISO/IEC 23008-12:2017 HEIF and AVIF (AV1 Image File Format) file format decoder and encoder. There is partial support for ISO/IEC 23008-12:2022 (2nd Edition) capabilities.
HEIF and AVIF are new image file formats employing HEVC (H.265) or AV1 image coding, respectively, for the best compression ratios currently possible.
libheif supports various codecs provided by plugins for image decoding and encoding.
This package contains the aomdec plugin that uses libaom to decode AV1 images.
libaom: https://aomedia.org/

Changes for libheif-plugin-aomdec versions:
Installed version: 1.20.2-1ubuntu0.5
Available version: 1.20.2-1ubuntu0.6

Version 1.20.2-1ubuntu0.6: 

  * SECURITY UPDATE: Integer overflow when parsing uncC.
    - debian/patches/CVE-2026-47709-1.patch: Prevent integer overflow
      when parsing uncC in libheif/codecs/uncompressed/unc_boxes.cc
    - debian/patches/CVE-2026-47709-2.patch: Reject unci images with no ispe
      box in libheif/image-items/unc_image.cc
    - CVE-2026-47709
  * SECURITY UPDATE: Integer overflow in inline mask size calculation
    - debian/patches/CVE-2026-47714.patch: Fix computation of size of inline
      region mask in libheif/region.cc
    - CVE-2026-47714
  * SECURITY UPDATE: OOB read in ImageItem_Grid::decode_grid_tile.
    - debian/patches/CVE-2026-48029.patch: Fix tile coordinates validation
      in rotated images in libheif/api/libheif/heif_tiling.cc and
      libheif/image-items/image_item.cc
    - CVE-2026-48029
  * SECURITY UPDATE: Unbounded heap allocation in sequence parser.
    - debian/patches/CVE-2026-50142.patch: Fix check against security limit
      in libheif/sequences/seq_boxes.cc and ../track.cc
    - CVE-2026-50142

    
  ---
  
  Technical description
Package: heif-thumbnailer
libheif is an ISO/IEC 23008-12:2017 HEIF and AVIF (AV1 Image File Format) file format decoder and encoder. There is partial support for ISO/IEC 23008-12:2022 (2nd Edition) capabilities.
HEIF and AVIF are new image file formats employing HEVC (H.265) or AV1 image coding, respectively, for the best compression ratios currently possible.
libheif supports various codecs provided by plugins for image decoding and encoding.
A thumbnailer for HEIF images that can be used by Nautilus is provided by this package.

Changes for heif-thumbnailer versions:
Installed version: 1.20.2-1ubuntu0.5
Available version: 1.20.2-1ubuntu0.6

Version 1.20.2-1ubuntu0.6: 

  * SECURITY UPDATE: Integer overflow when parsing uncC.
    - debian/patches/CVE-2026-47709-1.patch: Prevent integer overflow
      when parsing uncC in libheif/codecs/uncompressed/unc_boxes.cc
    - debian/patches/CVE-2026-47709-2.patch: Reject unci images with no ispe
      box in libheif/image-items/unc_image.cc
    - CVE-2026-47709
  * SECURITY UPDATE: Integer overflow in inline mask size calculation
    - debian/patches/CVE-2026-47714.patch: Fix computation of size of inline
      region mask in libheif/region.cc
    - CVE-2026-47714
  * SECURITY UPDATE: OOB read in ImageItem_Grid::decode_grid_tile.
    - debian/patches/CVE-2026-48029.patch: Fix tile coordinates validation
      in rotated images in libheif/api/libheif/heif_tiling.cc and
      libheif/image-items/image_item.cc
    - CVE-2026-48029
  * SECURITY UPDATE: Unbounded heap allocation in sequence parser.
    - debian/patches/CVE-2026-50142.patch: Fix check against security limit
      in libheif/sequences/seq_boxes.cc and ../track.cc
    - CVE-2026-50142


---

Technical description
Package: heif-gdk-pixbuf
libheif is an ISO/IEC 23008-12:2017 HEIF and AVIF (AV1 Image File Format) file format decoder and encoder. There is partial support for ISO/IEC 23008-12:2022 (2nd Edition) capabilities.
HEIF and AVIF are new image file formats employing HEVC (H.265) or AV1 image coding, respectively, for the best compression ratios currently possible.
libheif supports various codecs provided by plugins for image decoding and encoding.
A gdk-pixbuf loader module for applications such as "gpicview" and "pcmanfm" is provided by this package.

Changes for heif-gdk-pixbuf versions:
Installed version: 1.20.2-1ubuntu0.5
Available version: 1.20.2-1ubuntu0.6

Version 1.20.2-1ubuntu0.6: 

  * SECURITY UPDATE: Integer overflow when parsing uncC.
    - debian/patches/CVE-2026-47709-1.patch: Prevent integer overflow
      when parsing uncC in libheif/codecs/uncompressed/unc_boxes.cc
    - debian/patches/CVE-2026-47709-2.patch: Reject unci images with no ispe
      box in libheif/image-items/unc_image.cc
    - CVE-2026-47709
  * SECURITY UPDATE: Integer overflow in inline mask size calculation
    - debian/patches/CVE-2026-47714.patch: Fix computation of size of inline
      region mask in libheif/region.cc
    - CVE-2026-47714
  * SECURITY UPDATE: OOB read in ImageItem_Grid::decode_grid_tile.
    - debian/patches/CVE-2026-48029.patch: Fix tile coordinates validation
      in rotated images in libheif/api/libheif/heif_tiling.cc and
      libheif/image-items/image_item.cc
    - CVE-2026-48029
  * SECURITY UPDATE: Unbounded heap allocation in sequence parser.
    - debian/patches/CVE-2026-50142.patch: Fix check against security limit
      in libheif/sequences/seq_boxes.cc and ../track.cc
    - CVE-2026-50142

---


