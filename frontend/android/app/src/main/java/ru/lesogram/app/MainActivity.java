package ru.lesogram.app;

import android.os.Bundle;
import android.view.WindowManager;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Dark chrome to match the app theme: translucent status/nav bars
        // over the dark #020617 background (no white flash on launch).
        getWindow().setStatusBarColor(android.graphics.Color.parseColor("#020617"));
        getWindow().setNavigationBarColor(android.graphics.Color.parseColor("#020617"));
    }
}
