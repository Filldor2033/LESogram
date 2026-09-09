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

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Dark chrome to match the app theme (no white flash on launch).
        getWindow().setStatusBarColor(android.graphics.Color.parseColor("#020617"));
        getWindow().setNavigationBarColor(android.graphics.Color.parseColor("#020617"));

        /*
         * Voice messages: the WebView's getUserMedia fires the runtime
         * permission dialog only AFTER the native permission is granted —
         * asking first avoids the confusing double-deny flow.
         */
        ensureMicPermission();
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
}
