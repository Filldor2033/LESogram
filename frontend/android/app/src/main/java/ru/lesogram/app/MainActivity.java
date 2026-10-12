package ru.lesogram.app;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    private static final int REQ_MIC = 41;
    private static final int REQ_NOTIF = 42;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        /*
         * Branded chrome: deep slate bars with a green accent edge.
         * The status bar (camera cutout area) and the navigation bar
         * (gesture/button strip) sit on the panel color #0f172a with
         * a 2px green #22c55e bottom/top line drawn via the window
         * background — the web layer cannot paint behind system bars
         * once edge-to-edge is off, so the color comes from here.
         */
        getWindow().setStatusBarColor(
            android.graphics.Color.parseColor("#0f172a"));
        getWindow().setNavigationBarColor(
            android.graphics.Color.parseColor("#0f172a"));

        /*
         * Light (white) icons on the dark bars: clear the LIGHT
         * flags — their presence would request dark icons.
         */
        final android.view.View decor = getWindow().getDecorView();
        decor.setSystemUiVisibility(
            decor.getSystemUiVisibility()
            & ~android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            & ~android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);

        /*
         * Voice messages: the WebView's getUserMedia fires the runtime
         * permission dialog only AFTER the native permission is granted —
         * asking first avoids the confusing double-deny flow.
         */
        ensureMicPermission();

        /*
         * Android 13+: notification permission is runtime. Ask once on
         * launch so background message notifications can appear; a deny
         * (or "don't ask again") is non-fatal — the app keeps working.
         */
        ensureNotificationPermission();
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
