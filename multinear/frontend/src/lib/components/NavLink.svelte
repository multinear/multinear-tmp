<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    
    export let href: string;
    export let label: string;
</script>

<a {href} class="block">
    <Button variant="ghost" class="hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full">
        {label}
    </Button>
</a>
