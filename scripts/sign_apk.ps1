# Sign a rebuilt Aerial APK (v1 + v2 + v3)

Google's `dl.google.com` mirrors are often unreachable from mainland China, so
this script uses [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer),
which bundles `apksig` and `zipalign` and is downloadable from GitHub Releases.

```powershell
# 1. one-time: get a JDK 17 (Temurin) and uber-apk-signer
#    https://api.adoptium.net/v3/assets/latest/17/hotspot?os=windows&architecture=x64&image_type=jdk
#    https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar

# 2. one-time: create a signing key (keystore). KEEP THIS FILE.
keytool -genkeypair -keystore aerial.keystore -storepass aerial123 `
        -keypass aerial123 -alias aerial -keyalg RSA -keysize 2048 `
        -validity 10950 -dname "CN=Aerial TV, O=Aerial, C=CN"

# 3. sign (zipalign + v1 + v2 + v3)
java -jar uber-apk-signer-1.3.0.jar `
     --apks aerial-unsigned.apk --overwrite `
     --ks aerial.keystore --ksAlias aerial --ksPass aerial123 --ksKeyPass aerial123

# 4. verify
java -jar uber-apk-signer-1.3.0.jar --apks aerial-signed.apk --verify
```

## Why v2 is mandatory

`AndroidManifest.xml` declares `targetSdkVersion=34`. Android 11 (API 30) and
newer refuse to install an APK that targets SDK 30+ unless it carries an
APK Signature Scheme **v2 or v3** signature. A v1-only (JAR) signature is not
enough -- the install fails with `INSTALL_PARSE_FAILED_NO_CERTIFICATES`.

Modifying the APK always invalidates both the v1 manifest digests and the v2/v3
signing block, so re-signing is unavoidable.

## Consequences of re-signing

The upstream Aerial builds are signed with the author's Android debug key
(`CN=Android Debug`). That private key is not public, so a rebuilt APK can never
share its signature. In practice:

- the new APK **cannot upgrade** an installed Aerial build;
- you must **uninstall the old Aerial first**, which wipes its settings;
- the signing certificate fingerprint changes (Android treats it as a different
  app identity for update purposes).

If you only want to add videos to your own TV, you do **not** need to rebuild the
APK at all -- use the upload path described in `docs/analysis.md`, which keeps
the official signature intact.
