package ru.lesogram.app;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.webkit.PermissionRequest;

import com.getcapacitor.BridgeWebChromeClient;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.getcapacitor.BridgeActivity;
import com.getcapacitor.Bridge;
import com.getcapacitor.BridgeWebView;

public class MainActivity extends BridgeActivity {

    private static final int REQ_MIC = 41;
    private static final int REQ_NOTIF = 42;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        /*
         * Android 15+ (targetSdk 35+) forces edge-to-edge and IGNORES
         * setStatusBarColor — the bars stay translucent gray. Instead:
         * draw behind the bars ourselves. The window background
         * (panel slate #0f172a) shows through the now-transparent
         * status/navigation bars, and the WebView content already
         * respects env(safe-area-inset-*) paddings in CSS.
         */
        getWindow().setStatusBarColor(
            android.graphics.Color.TRANSPARENT);
        getWindow().setNavigationBarColor(
            android.graphics.Color.TRANSPARENT);
        getWindow().setBackgroundDrawable(
            new android.graphics.drawable.ColorDrawable(
                android.graphics.Color.parseColor("#0f172a")));

        /*
         * Light (white) icons on the dark background:
         * WindowInsetsController is the modern API (35+); the
         * legacy system-ui flags cover older versions.
         */
        final android.view.Window window = getWindow();
        final android.view.View decor = window.getDecorView();
        decor.setSystemUiVisibility(
            decor.getSystemUiVisibility()
            & ~android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            & ~android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        androidx.core.view.WindowCompat
            .getInsetsController(window, decor)
            .setAppearanceLightStatusBars(false);
        androidx.core.view.WindowCompat
            .getInsetsController(window, decor)
            .setAppearanceLightNavigationBars(false);

        /*
         * Voice messages: the WebView's getUserMedia fires the runtime
         * permission dialog only AFTER the native permission is granted —
         * asking first avoids the confusing double-deny flow.
         */
        ensureMicPermission();

        /*
         * Robust getUserMedia grant: Capacitor's own WebChromeClient
         * routes onPermissionRequest through a single-slot listener
         * that can drop the grant (observed as NotAllowedError
         * "Permission denied" on Android 15 WebView with RECORD_AUDIO
         * fully granted). Install our client on top: when the WebView
         * asks for audio capture and the native permission is granted,
         * answer immediately.
         */
        /*
         * Subclass Capacitor's client so all its behavior (alerts,
         * file choosers, console relay) stays intact — we only take
         * over the audio permission answer.
         */
        getBridge().getWebView().setWebChromeClient(new BridgeWebChromeClient(getBridge()) {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                final boolean audio =
                    java.util.Arrays.asList(request.getResources())
                        .contains("android.webkit.resource.AUDIO_CAPTURE");

                if (audio && micGranted()) {
                    request.grant(request.getResources());
                } else {
                    super.onPermissionRequest(request);
                }
            }
        });

        /*
         * Android 13+: notification permission is runtime. Ask once on
         * launch so background message notifications can appear; a deny
         * (or "don't ask again") is non-fatal — the app keeps working.
         */
        ensureNotificationPermission();
    }

    private boolean micGranted() {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED;
    }

    private void ensureMicPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED) {
            return;
        }
        ActivityCompat.requestPermissions(
                this,
                new String[]{Manifest.permission.RECORD_AUDIO},
                REQ_MIC
        );
    }

    private void ensureNotificationPermission() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            return;
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                == PackageManager.PERMISSION_GRANTED) {
            return;
        }
        ActivityCompat.requestPermissions(
                this,
                new String[]{Manifest.permission.POST_NOTIFICATIONS},
                REQ_NOTIF
        );
    }
}
