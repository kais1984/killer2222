import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart' show defaultTargetPlatform, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (defaultTargetPlatform == TargetPlatform.android) {
      return android;
    }
    return android;
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyDR5AyzEvHz9GlGolAf0ITUWQO92CaK_PU',
    appId: '1:1010092920868:android:e5500ee0b3290a5d8ec8b1',
    messagingSenderId: '1010092920868',
    projectId: 'driver-log-book-58c90',
    storageBucket: 'driver-log-book-58c90.firebasestorage.app',
  );
}
