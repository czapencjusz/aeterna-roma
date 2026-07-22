using System;

namespace GladiatusOffline
{
    public static class WebAssets
    {
        public static string IndexHtml = @"<!DOCTYPE html>
<html lang=""en"">
<head>
    <meta charset=""UTF-8"">
    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">
    <title>Aeterna Roma - Hero of Rome</title>
    <link href=""https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Cinzel+Decorative:wght@700&family=Philosopher:ital,wght@0,400;0,700;1,400&display=swap"" rel=""stylesheet"">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }

        :root {
            --bg-main: #0c0908;
            --bg-gradient: radial-gradient(circle at 50% 30%, #291c14 0%, #0d0907 80%);
            --bg-card: rgba(26, 17, 10, 0.85);
            --sub-bg: rgba(30, 20, 13, 0.7);
            --bg-header: #1c130d;
            --text-primary: #e5d3b3;
            --text-accent: #ffd700;
            --border-color: #8c6738;
            --panel-header-bg: linear-gradient(90deg, #4a1515 0%, #1a0808 100%);
            --btn-bg: linear-gradient(180deg, #6e1c1c 0%, #3d0c0c 100%);
            --btn-gold-bg: linear-gradient(180deg, #a67c1e 0%, #573e0e 100%);
        }

        body.theme-DarkImperial {
            --bg-main: #0c0908;
            --bg-gradient: radial-gradient(circle at 50% 30%, #291c14 0%, #0d0907 80%);
            --bg-card: rgba(26, 17, 10, 0.85);
            --sub-bg: rgba(30, 20, 13, 0.7);
            --bg-header: #1c130d;
            --text-primary: #e5d3b3;
            --text-accent: #ffd700;
            --border-color: #8c6738;
            --panel-header-bg: linear-gradient(90deg, #4a1515 0%, #1a0808 100%);
            --btn-bg: linear-gradient(180deg, #6e1c1c 0%, #3d0c0c 100%);
            --btn-gold-bg: linear-gradient(180deg, #a67c1e 0%, #573e0e 100%);
        }

        body.theme-RomanParchment {
            --bg-main: #f4ecd8;
            --bg-gradient: radial-gradient(circle at 50% 30%, #ede0c4 0%, #dfd0b0 80%);
            --bg-card: #ede0c4;
            --sub-bg: #e2d2b0;
            --bg-header: #dfd0b0;
            --text-primary: #2c1a0c;
            --text-accent: #8b0000;
            --border-color: #a88556;
            --panel-header-bg: linear-gradient(90deg, #a88556 0%, #6e5230 100%);
            --btn-bg: linear-gradient(180deg, #8b0000 0%, #4a0000 100%);
            --btn-gold-bg: linear-gradient(180deg, #c59b27 0%, #7a5e12 100%);
        }

        body.theme-ColosseumCrimson {
            --bg-main: #140505;
            --bg-gradient: radial-gradient(circle at 50% 30%, #3b0a0a 0%, #140505 80%);
            --bg-card: rgba(35, 10, 10, 0.85);
            --sub-bg: rgba(45, 15, 15, 0.7);
            --bg-header: #280808;
            --text-primary: #f5d6d6;
            --text-accent: #ff4d4d;
            --border-color: #a83232;
            --panel-header-bg: linear-gradient(90deg, #7a1515 0%, #3b0808 100%);
            --btn-bg: linear-gradient(180deg, #a81c1c 0%, #520c0c 100%);
            --btn-gold-bg: linear-gradient(180deg, #d49b27 0%, #7a5712 100%);
        }

        body.theme-LegionEmerald {
            --bg-main: #06140b;
            --bg-gradient: radial-gradient(circle at 50% 30%, #0d381c 0%, #06140b 80%);
            --bg-card: rgba(10, 30, 18, 0.85);
            --sub-bg: rgba(15, 40, 24, 0.7);
            --bg-header: #0a2414;
            --text-primary: #d4f5e0;
            --text-accent: #4dff91;
            --border-color: #2e8b57;
            --panel-header-bg: linear-gradient(90deg, #15522e 0%, #082915 100%);
            --btn-bg: linear-gradient(180deg, #1ca857 0%, #0c522a 100%);
            --btn-gold-bg: linear-gradient(180deg, #b8a027 0%, #695a12 100%);
        }

        body.theme-TyrianPurple {
            --bg-main: #120614;
            --bg-gradient: radial-gradient(circle at 50% 30%, #310c38 0%, #120614 80%);
            --bg-card: rgba(28, 10, 33, 0.85);
            --sub-bg: rgba(38, 15, 45, 0.7);
            --bg-header: #200a26;
            --text-primary: #f1d6f5;
            --text-accent: #e066ff;
            --border-color: #8a2be2;
            --panel-header-bg: linear-gradient(90deg, #5c157a 0%, #2b083b 100%);
            --btn-bg: linear-gradient(180deg, #7b1ca8 0%, #3e0c52 100%);
            --btn-gold-bg: linear-gradient(180deg, #d49b27 0%, #7a5712 100%);
        }

        body {
            background: var(--bg-main);
            background-image: var(--bg-gradient);
            color: var(--text-primary);
            font-family: 'Philosopher', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            transition: background 0.3s ease, color 0.3s ease;
        }

        header {
            background: var(--bg-header);
            border-bottom: 2px solid var(--border-color);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.8);
        }

        .subtab-btn {
            background: rgba(0,0,0,0.4);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            font-family: 'Cinzel', serif;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .subtab-btn:hover {
            background: var(--sub-bg);
            color: var(--text-accent);
        }
        .subtab-btn.active {
            background: var(--btn-gold-bg);
            color: #fff;
            border-color: var(--text-accent);
        }

        .btn-roman {
            background: var(--btn-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .btn-roman:hover {
            filter: brightness(1.2);
            box-shadow: 0 0 10px rgba(255,215,0,0.3);
        }
        .btn-gold {
            background: var(--btn-gold-bg);
            color: #fff;
        }
    </style>
</head>
<body class=""theme-DarkImperial"">
    <!-- Rest of WebAssets HTML omitted for brevity in snippet -->
</body>
</html>";
    }
}
