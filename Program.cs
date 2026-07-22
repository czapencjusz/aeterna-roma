using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace GladiatusOffline
{
    class Program
    {
        public static Action ToggleFullscreenAction;

        // Win32: create a named mutex to ensure only one instance runs
        [DllImport("kernel32.dll")]
        static extern IntPtr CreateMutex(IntPtr lpMutexAttributes, bool bInitialOwner, string lpName);
        [DllImport("kernel32.dll")]
        static extern int GetLastError();
        const int ERROR_ALREADY_EXISTS = 183;

        [STAThread]
        static void Main(string[] args)
        {
            // Single-instance guard: if server is already running, just open browser
            IntPtr mutex = CreateMutex(IntPtr.Zero, true, "AeternaRoma_Server_Mutex");
            if (GetLastError() == ERROR_ALREADY_EXISTS)
            {
                // Another instance is already running the server; just open the UI
                LaunchAppWindow("http://127.0.0.1:8080/");
                return;
            }

            // Start HTTP server on background thread
            Server server = new Server(8080);
            Thread serverThread = new Thread(() => server.Start());
            serverThread.IsBackground = true;
            serverThread.Start();

            // Wait until HTTP server successfully binds
            server.ServerStartedEvent.WaitOne(5000);
            string url = server.BoundUrl ?? "http://127.0.0.1:8080/";

            // Launch game in a chromeless standalone window via Edge/Chrome app mode
            LaunchAppWindow(url);

            // Keep the process alive with a hidden form message loop.
            // This keeps the background server thread alive and responsive.
            // The process will only exit when the user kills it via Task Manager
            // or when Windows shuts down.
            Application.Run(new HiddenForm());
        }

        private static void LaunchAppWindow(string url)
        {
            // Strategy: Try Edge app mode first, then Chrome app mode, then default browser
            // App mode = chromeless window (no address bar, no tabs) — looks like a native app

            // 1) Try Microsoft Edge (always present on Windows 10/11)
            string edgePath = FindEdgePath();
            if (edgePath != null)
            {
                try
                {
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = edgePath,
                        Arguments = "--app=" + url + " --new-window --disable-extensions",
                        UseShellExecute = false
                    });
                    return;
                }
                catch { }
            }

            // 2) Try Google Chrome
            string chromePath = FindChromePath();
            if (chromePath != null)
            {
                try
                {
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = chromePath,
                        Arguments = "--app=" + url + " --new-window --disable-extensions",
                        UseShellExecute = false
                    });
                    return;
                }
                catch { }
            }

            // 3) Fallback: open default browser (will have address bar, but at least it works)
            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = url,
                    UseShellExecute = true
                });
            }
            catch { }
        }

        private static string FindEdgePath()
        {
            string[] candidates = new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                    "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                    "Microsoft", "Edge", "Application", "msedge.exe"),
                @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                @"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            };

            foreach (string path in candidates)
            {
                if (File.Exists(path)) return path;
            }
            return null;
        }

        private static string FindChromePath()
        {
            string[] candidates = new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                    "Google", "Chrome", "Application", "chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                    "Google", "Chrome", "Application", "chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "Google", "Chrome", "Application", "chrome.exe"),
                @"C:\Program Files\Google\Chrome\Application\chrome.exe",
                @"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            };

            foreach (string path in candidates)
            {
                if (File.Exists(path)) return path;
            }
            return null;
        }
    }

    // Invisible form that keeps the process alive via the WinForms message pump
    class HiddenForm : Form
    {
        private NotifyIcon trayIcon;

        public HiddenForm()
        {
            this.ShowInTaskbar = false;
            this.WindowState = FormWindowState.Minimized;
            this.FormBorderStyle = FormBorderStyle.None;
            this.Opacity = 0;
            this.Size = new System.Drawing.Size(0, 0);

            // System tray icon so the user can re-open or quit the game
            trayIcon = new NotifyIcon();
            trayIcon.Text = "Aeterna Roma";
            trayIcon.Icon = System.Drawing.SystemIcons.Shield;
            trayIcon.Visible = true;
            trayIcon.DoubleClick += OnTrayDoubleClick;

            ContextMenuStrip menu = new ContextMenuStrip();
            menu.Items.Add("Open Game Window", null, OnOpenGame);
            menu.Items.Add("Exit Aeterna Roma", null, OnExit);
            trayIcon.ContextMenuStrip = menu;
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            this.Visible = false;
            this.Hide();
        }

        private void OnTrayDoubleClick(object sender, EventArgs e)
        {
            OnOpenGame(sender, e);
        }

        private void OnOpenGame(object sender, EventArgs e)
        {
            // Re-launch a new app-mode window pointing at the running server
            string edgePath = FindEdgePath();
            if (edgePath != null)
            {
                try
                {
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = edgePath,
                        Arguments = "--app=http://127.0.0.1:8080/ --new-window --disable-extensions",
                        UseShellExecute = false
                    });
                    return;
                }
                catch { }
            }
            // Fallback
            try
            {
                Process.Start(new ProcessStartInfo { FileName = "http://127.0.0.1:8080/", UseShellExecute = true });
            }
            catch { }
        }

        private void OnExit(object sender, EventArgs e)
        {
            trayIcon.Visible = false;
            trayIcon.Dispose();
            Application.Exit();
        }

        private static string FindEdgePath()
        {
            string[] candidates = new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                    "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                    "Microsoft", "Edge", "Application", "msedge.exe"),
                @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                @"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            };

            foreach (string path in candidates)
            {
                if (File.Exists(path)) return path;
            }
            return null;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && trayIcon != null)
            {
                trayIcon.Visible = false;
                trayIcon.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
