from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,DeleteView,UpdateView
from charging_center.models import *
from charging_center.forms import *
# Create your views here.

class ChargingStationView(CreateView):
    model = ChargingStations
    form_class = ChargingRegister
    template_name = "station_creation.html"
    success_url = reverse_lazy('slot-list')
    def form_valid(self, form):
        return super().form_valid(form)

class ChargingListView(ListView):
    model = ChargingStations
    template_name = "station_list.html"
    context_object_name = 'stations'


class SloteCreationView(CreateView):
    model = ChargingSlot
    form_class = ChargingsloteCreation
    template_name = "slot_creation.html"

    def form_valid(self, form):
        form.instance.station = get_object_or_404(
            ChargingStations,
            id=self.kwargs.get("station_id")
        )
        return super().form_valid(form) 

    def get_success_url(self):
        return reverse_lazy(
            "slot-list",
            kwargs={"station_id": self.kwargs.get("station_id")}
        )

class SlotListView(ListView):
    model = ChargingSlot
    template_name = "slot_list.html"
    context_object_name = 'slots'

    def get_queryset(self):
        return ChargingSlot.objects.filter(
            station_id=self.kwargs.get("station_id")
        ).order_by("start_time")
    


class SlotUpdateView(UpdateView):
    model = ChargingSlot
    form_class = ChargingsloteCreation  
    template_name = "slot_update.html"  
    context_object_name = "slot"

    def get_queryset(self):
        station_id = self.kwargs.get("station_id")
        return ChargingSlot.objects.filter(station_id=station_id)

    def get_success_url(self):
        return reverse_lazy(
            "slot-list",
            kwargs={"station_id": self.kwargs.get("station_id")}
        )


class SlotDeleteView(DeleteView):
    model = ChargingSlot
    template_name = "slot_confirm_delete.html"
    context_object_name = "slot"

    def get_queryset(self):
        station_id = self.kwargs.get("station_id")
        return ChargingSlot.objects.filter(station_id=station_id)
    
    def get_success_url(self):
        return reverse_lazy(
            "slot-list",
            kwargs={"station_id": self.kwargs.get("station_id")}
        )