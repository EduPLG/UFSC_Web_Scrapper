from playwright.sync_api import Page


def next_page_zapimoveis(page: Page) -> bool:
    btn = page.locator('button[data-testid="next-page"]')
    if not btn.count():
        return False

    if btn.get_attribute("disabled"):
        return False

    try:
        btn.scroll_into_view_if_needed()
        btn.click(timeout=5000),
        page.wait_for_load_state("load", timeout=7000),
        return True
    except Exception as e:
        print(f"Zapimoveis: erro ao tentar avançar -> {e}")
        return False


def next_page_imoveisweb(page: Page) -> bool:
    link = page.locator('a[data-qa="PAGING_NEXT"]')
    if not link.count():
        return False

    classes = (link.get_attribute("class")) or ""
    if "disabled" in classes:
        return False

    try:
        link.scroll_into_view_if_needed()
        link.click(timeout=5000),
        page.wait_for_load_state("load", timeout=7000)
        return True
    except Exception as e:
        print(f"imoveisweb: erro ao tentar avançar -> {e}")
        return False


def next_page_brognoli(page: Page) -> bool:
    pagination = page.locator("ul.pagination")
    if not pagination.count():
        return False

    pagination.scroll_into_view_if_needed()
    active = pagination.locator("a.active").text_content()      # Get active page number
    next_btn = pagination.locator(f'text="{int(active) + 1}"')  # Get next page button

    if not next_btn.count():
        return False

    try:
        next_btn.click(timeout=5000)                                # Click the button
        page.wait_for_load_state("load", timeout=7000)
        return True
    except Exception as e:
        print(f"brognoli: erro ao tentar avançar -> {e}")
        return False
