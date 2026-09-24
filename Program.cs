using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

namespace GladiatusOffline
{
    // Aeterna Roma is a self-contained HTML game (game.html) that runs entirely in the browser
    // and saves to the browser's local storage. This launcher only unpacks the embedded page
    // and opens it in a chromeless Edge/Chrome app window, then exits. Nothing keeps running
    // in the background and no network ports are opened.
    static class Program
    {
        const string GameResourceName = "AeternaRoma.game.html";

        [STAThread]
        static void Main()
        {
            string gamePath;
            try
            {
                gamePath = ExtractGame();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Could not prepare the game files:\n\n" + ex.Message,
                    "Aeterna Roma", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            string url = new Uri(gamePath).AbsoluteUri;

            // App mode = chromeless window (no address bar, no tabs) that looks like a native app.
            if (TryLaunchAppWindow(FindFirstExisting(EdgeCandidates()), url)) return;
            if (TryLaunchAppWindow(FindFirstExisting(ChromeCandidates()), url)) return;

            // Fallback: open the page in the default browser.
            try
            {
                Process.Start(new ProcessStartInfo { FileName = gamePath, UseShellExecute = true });
            }
            catch (Exception ex)
            {
                MessageBox.Show("Could not open a browser for the game. You can open this file manually:\n\n" + gamePath + "\n\n" + ex.Message,
                    "Aeterna Roma", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        // Writes the embedded game page to %LOCALAPPDATA%\AeternaRoma\game.html.
        // The page lives at a fixed path so the browser keeps the same local storage (save data) between launches.
        private static string ExtractGame()
        {
            byte[] content;
            using (Stream resource = Assembly.GetExecutingAssembly().GetManifestResourceStream(GameResourceName))
            {
                if (resource == null) throw new InvalidOperationException("The game page is missing from the executable. Rebuild it with build.bat.");
                using (MemoryStream buffer = new MemoryStream())
                {
                    resource.CopyTo(buffer);
                    content = buffer.ToArray();
                }
            }

            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "AeternaRoma");
            Directory.CreateDirectory(dir);
            string path = Path.Combine(dir, "game.html");

            if (!File.Exists(path) || !ContentEquals(File.ReadAllBytes(path), content))
            {
                string tempPath = path + ".tmp";
                File.WriteAllBytes(tempPath, content);
                if (File.Exists(path)) File.Replace(tempPath, path, null);
                else File.Move(tempPath, path);
            }
            return path;
        }

        private static bool ContentEquals(byte[] a, byte[] b)
        {
            if (a.Length != b.Length) return false;
            for (int i = 0; i < a.Length; i++)
            {
                if (a[i] != b[i]) return false;
            }
            return true;
        }

        private static bool TryLaunchAppWindow(string browserPath, string url)
        {
            if (browserPath == null) return false;
            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = browserPath,
                    Arguments = "--app=\"" + url + "\" --new-window",
                    UseShellExecute = false
                });
                return true;
            }
            catch
            {
                return false;
            }
        }

        private static string[] EdgeCandidates()
        {
            return new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Microsoft", "Edge", "Application", "msedge.exe")
            };
        }

        private static string[] ChromeCandidates()
        {
            return new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Google", "Chrome", "Application", "chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Google", "Chrome", "Application", "chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Google", "Chrome", "Application", "chrome.exe")
            };
        }

        private static string FindFirstExisting(string[] candidates)
        {
            foreach (string path in candidates)
            {
                if (!string.IsNullOrEmpty(path) && File.Exists(path)) return path;
            }
            return null;
        }
    }
}
