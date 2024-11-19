<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { page } from "$app/stores";
    export let href: string;
    export let label: string;

    $: isActive = (
        href === $page.url.pathname ||
        href.split('#')[0].startsWith(`${$page.url.pathname}`) ||
        `${href.split('#')[0]}/`.startsWith(`${$page.url.pathname}`) ||
        (href === '/' && $page.url.pathname.startsWith('/dashboard'))
    );
</script>

<a {href} class="block">
    <Button
        variant="ghost"
        class="hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full {isActive ? 'active-nav' : ''}"
    >
        {label}
    </Button>
</a>
<style>
    :global(.active-nav) {
        text-decoration: underline;
        text-underline-offset: 2px;
    }
</style>

