import json
from pathlib import Path
import threading
import customtkinter as ctk
from tkinter import messagebox
from urllib.parse import urlparse

from src.monitor import check_api
from src.health_check import evaluate_health


# ---------- APPEARANCE ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Store apis.json beside frontend.py
APIS_FILE = Path(__file__).resolve().parent / "apis.json"


def load_endpoints():
    """Load saved endpoint names and URLs."""
    if not APIS_FILE.exists():
        return []

    try:
        with APIS_FILE.open("r", encoding="utf-8") as file:
            saved_endpoints = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"Could not load saved endpoints: {error}")
        return []

    if not isinstance(saved_endpoints, list):
        print("Invalid apis.json format. Expected a list.")
        return []

    endpoints = []

    for item in saved_endpoints:
        if (
            isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and isinstance(item.get("url"), str)
        ):
            endpoints.append({
                "name": item["name"],
                "url": item["url"],
                "health": "Not checked",
                "status_code": None,
                "response_time_ms": None,
                "error": None
            })

    return endpoints


def save_endpoints(endpoints):
    """Save endpoint names and URLs to apis.json."""
    saved_endpoints = [
        {
            "name": endpoint["name"],
            "url": endpoint["url"]
        }
        for endpoint in endpoints
    ]

    try:
        with APIS_FILE.open("w", encoding="utf-8") as file:
            json.dump(saved_endpoints, file, indent=4)
        return True

    except OSError as error:
        print(f"Could not save endpoints: {error}")
        return False



def start_app():
    app = ctk.CTk()
    app.title("API Health Monitor")
    app.geometry("1100x720")
    app.minsize(900, 600)

    # Load saved endpoints from apis.json.
    endpoints = load_endpoints()

    # ---------- HEADER ----------
    header = ctk.CTkFrame(app, fg_color="transparent")
    header.pack(fill="x", padx=28, pady=(24, 12))

    ctk.CTkLabel(
        header,
        text="API Health Monitor",
        font=("Arial", 28, "bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header,
        text="Monitor endpoints. Track availability. Spot issues.",
        text_color="gray"
    ).pack(anchor="w", pady=(4, 0))

    # ---------- SUMMARY CARDS ----------
    cards = ctk.CTkFrame(app, fg_color="transparent")
    cards.pack(fill="x", padx=28, pady=12)

    cards.grid_columnconfigure((0, 1, 2), weight=1)

    def create_card(column, title, value, color):
        card = ctk.CTkFrame(cards, corner_radius=12)
        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(0 if column == 0 else 8, 0)
        )

        ctk.CTkLabel(
            card,
            text=title,
            text_color="gray"
        ).pack(anchor="w", padx=18, pady=(16, 4))

        number = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 28, "bold"),
            text_color=color
        )
        number.pack(anchor="w", padx=18, pady=(0, 16))

        return number

    total_value = create_card(
        0, "TOTAL ENDPOINTS", "0", "#60A5FA"
    )
    healthy_value = create_card(
        1, "HEALTHY", "0", "#34D399"
    )
    issues_value = create_card(
        2, "ISSUES", "0", "#F87171"
    )

    # ---------- ADD ENDPOINT FORM ----------
    add_frame = ctk.CTkFrame(app, corner_radius=12)
    add_frame.pack(fill="x", padx=28, pady=12)

    ctk.CTkLabel(
        add_frame,
        text="Add an endpoint",
        font=("Arial", 18, "bold")
    ).pack(anchor="w", padx=18, pady=(16, 10))

    form = ctk.CTkFrame(add_frame, fg_color="transparent")
    form.pack(fill="x", padx=18, pady=(0, 16))

    form.grid_columnconfigure(0, weight=1)
    form.grid_columnconfigure(1, weight=2)

    name_entry = ctk.CTkEntry(
        form,
        placeholder_text="API name (e.g. JSONPlaceholder)"
    )
    name_entry.grid(
        row=0, column=0, sticky="ew", padx=(0, 8)
    )

    url_entry = ctk.CTkEntry(
        form,
        placeholder_text="URL (https://example.com/api)"
    )
    url_entry.grid(
        row=0, column=1, sticky="ew", padx=8
    )

    # ---------- ENDPOINT LIST ----------
    list_frame = ctk.CTkFrame(app, corner_radius=12)
    list_frame.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=(4, 12)
    )

    list_header = ctk.CTkFrame(
        list_frame,
        fg_color="transparent"
    )
    list_header.pack(fill="x", padx=18, pady=16)

    ctk.CTkLabel(
        list_header,
        text="Monitored endpoints",
        font=("Arial", 18, "bold")
    ).pack(side="left")

    endpoint_count = ctk.CTkLabel(
        list_header,
        text="0 endpoints",
        text_color="gray"
    )
    endpoint_count.pack(side="right")

    rows_frame = ctk.CTkScrollableFrame(
        list_frame,
        fg_color="transparent"
    )
    rows_frame.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 12)
    )

    # ---------- FOOTER / STATUS ----------
    footer = ctk.CTkFrame(app, fg_color="transparent")
    footer.pack(fill="x", padx=28, pady=(0, 20))

    status_label = ctk.CTkLabel(
        footer,
        text="Ready — add an endpoint to begin.",
        text_color="gray"
    )
    status_label.pack(side="left")

    # ---------- SUMMARY UPDATE ----------
    def refresh_summary():
        total_value.configure(text=str(len(endpoints)))

        healthy_count = sum(
            endpoint["health"] == "Healthy"
            for endpoint in endpoints
        )

        issues_count = sum(
            endpoint["health"] in ("Degraded", "Down")
            for endpoint in endpoints
        )

        healthy_value.configure(text=str(healthy_count))
        issues_value.configure(text=str(issues_count))

        endpoint_count.configure(
            text=f"{len(endpoints)} endpoint(s)"
        )

    # ---------- RENDER ENDPOINTS ----------
    def render_endpoints():
        for widget in rows_frame.winfo_children():
            widget.destroy()

        if not endpoints:
            ctk.CTkLabel(
                rows_frame,
                text="No endpoints added yet.\nAdd your first API above.",
                text_color="gray",
                font=("Arial", 14)
            ).pack(pady=45)

            return

        for endpoint in endpoints:
            row = ctk.CTkFrame(
                rows_frame,
                corner_radius=8
            )
            row.pack(fill="x", pady=5, padx=2)

            details = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            details.pack(
                side="left",
                fill="x",
                expand=True,
                padx=14,
                pady=10
            )

            ctk.CTkLabel(
                details,
                text=endpoint["name"],
                font=("Arial", 14, "bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=endpoint["url"],
                text_color="gray"
            ).pack(anchor="w", pady=(3, 0))

            health = endpoint["health"]

            if health == "Healthy":
                color = "#34D399"
            elif health == "Degraded":
                color = "#FBBF24"
            elif health == "Down":
                color = "#F87171"
            else:
                color = "gray"

            if endpoint["response_time_ms"] is not None:
                status_text = (
                    f'{health} · '
                    f'{endpoint["response_time_ms"]:.0f} ms'
                )
            elif endpoint["status_code"] is not None:
                status_text = (
                    f'{health} · HTTP '
                    f'{endpoint["status_code"]}'
                )
            elif endpoint["error"]:
                status_text = f"{health} · Error"
            else:
                status_text = health

            ctk.CTkLabel(
                row,
                text=status_text,
                text_color=color
            ).pack(side="left", padx=12)

            ctk.CTkButton(
                row,
                text="Remove",
                width=75,
                fg_color="#7F1D1D",
                hover_color="#991B1B",
                command=lambda item=endpoint: remove_endpoint(item)
            ).pack(side="right", padx=12, pady=10)

    # ---------- ADD ENDPOINT ----------
    def add_endpoint():
        name = name_entry.get().strip()
        url = url_entry.get().strip()

        if not name or not url:
            messagebox.showwarning(
                "Missing information",
                "Please enter both an API name and URL.",
                parent=app
            )
            return

        parsed = urlparse(url)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.netloc
        ):
            messagebox.showwarning(
                "Invalid URL",
                "Enter a valid URL beginning with http:// or https://",
                parent=app
            )
            return

        if any(item["url"] == url for item in endpoints):
            messagebox.showwarning(
                "Duplicate endpoint",
                "This URL is already in the list.",
                parent=app
            )
            return

        endpoints.append({
            "name": name,
            "url": url,
            "health": "Not checked",
            "status_code": None,
            "response_time_ms": None,
            "error": None
        })
        if not save_endpoints(endpoints):
            messagebox.showerror(
                "Save failed",
                "The endpoint was added for this session, "
                "but could not be saved to apis.json.",
                parent=app
            )

        name_entry.delete(0, "end")
        url_entry.delete(0, "end")

        render_endpoints()
        refresh_summary()

        status_label.configure(
            text=f"Added {name}. It has not been checked yet."
        )

    # ---------- REMOVE ENDPOINT ----------
    def remove_endpoint(endpoint):
        if endpoint in endpoints:
            endpoints.remove(endpoint)

        if not save_endpoints(endpoints):
            messagebox.showerror(
                "Save failed",
                "The endpoint was removed for this session, "
                "but the updated list could not be saved.",
                parent=app
            )    

        render_endpoints()
        refresh_summary()

        status_label.configure(text="Endpoint removed.")

    # ---------- FINISH MONITORING ----------
    def finish_checks(results):
        for endpoint, result, health in results:
            # Do not update an endpoint that has been removed.
            if endpoint not in endpoints:
                continue

            endpoint["health"] = health
            endpoint["status_code"] = result["status_code"]
            endpoint["response_time_ms"] = (
                result["response_time_ms"]
            )
            endpoint["error"] = result["error"]

        render_endpoints()
        refresh_summary()

        check_all_button.configure(state="normal")

        status_label.configure(
            text=(
                f"Monitoring complete — "
                f"{len(results)} endpoint(s) checked."
            )
        )

    # ---------- CHECK ALL ENDPOINTS ----------
    def check_all():
        if not endpoints:
            messagebox.showinfo(
                "No endpoints",
                "Add at least one API endpoint first.",
                parent=app
            )
            return

        # Snapshot the current endpoints before starting.
        endpoints_to_check = endpoints.copy()

        check_all_button.configure(state="disabled")
        status_label.configure(text="Checking endpoints...")

        def run_checks():
            results = []

            for endpoint in endpoints_to_check:
                try:
                    result = check_api(endpoint["url"])
                    health = evaluate_health(result)

                except Exception as error:
                    result = {
                        "url": endpoint["url"],
                        "status_code": None,
                        "response_time_ms": None,
                        "reachable": False,
                        "error": str(error)
                    }
                    health = "Down"

                results.append((endpoint, result, health))

            # Tkinter UI updates must run on the GUI thread.
            app.after(
                0,
                lambda: finish_checks(results)
            )

        threading.Thread(
            target=run_checks,
            daemon=True
        ).start()

    # ---------- BUTTONS ----------
    ctk.CTkButton(
        form,
        text="Add endpoint",
        command=add_endpoint
    ).grid(
        row=1,
        column=0,
        sticky="w",
        pady=(10, 0)
    )

    check_all_button = ctk.CTkButton(
        footer,
        text="Check all",
        command=check_all,
        width=120
    )
    check_all_button.pack(side="right")

    # Draw the initial empty state.
    render_endpoints()
    refresh_summary()

    # Start the GUI event loop.
    app.mainloop()
